# -*- coding: utf-8 -*-
"""
config.ini контроллера moduleBox -> YAML-описание схемы подключения.

Состав контроллера берётся из [SYSTEM], [LAN] и [SLOT_n]; тип нагрузки,
её подпись и флаги — из комментария (`;...`) внутри секции слота.
База нагрузок: .claude/skills/connection-scheme/loads.yaml.

Грамматика комментария слота:
    ;<тип>[_xN] [подпись...] [флаги...] [<тип2> [подпись...]]
  - тип — ключ из loads (регистр не важен), _xN — N одинаковых нагрузок;
  - если типов нет — берутся нагрузки по умолчанию для mode;
  - флаги (OCjumper, NPN, PNP, NO, NC, DCDC) распознаются где угодно;
  - остальные слова — подпись нагрузки, к которой они ближе слева.
Комментарий [SYSTEM]: `;12v 100w mountPlate` -> блок питания 12V 100W под
контроллером и пометка «монтажная плита».

Запуск:
  python tools/scheme_gen/from_config.py <config.ini> [-o out.scheme.yaml] [--force]
По умолчанию результат кладётся рядом: <deviceName>.scheme.yaml.
Существующий YAML не перезаписывается без --force (в нём ручные правки).
"""

import sys
import os
import re
import argparse

try:
    import yaml
except ImportError:
    sys.exit("Нужен PyYAML:  python -m pip install pyyaml")

HERE = os.path.dirname(os.path.abspath(__file__))
LOADS_DEFAULT = os.path.normpath(os.path.join(
    HERE, "..", "..", ".claude", "skills", "connection-scheme", "loads.yaml"))

VOLT_RE = re.compile(r"^(\d+(?:[.,]\d+)?)\s*[vVвВ]$")
TYPE_RE = re.compile(r"^([A-Za-z][A-Za-z0-9]*?)(?:_x(\d+))?$")
TOPIC_RE = re.compile(r"^(\w+?)_(\d+)/(event|action)/(\w+)(?::(.*))?$")

# подписи на датчиках по действию-приёмнику crosslink
ACTION_NOTES = {
    "setHomingSensor": "датчик нуля {dst}",
    "setUpLimit":      "верхний концевик {dst}",
    "setDownLimit":    "нижний концевик {dst}",
}


def warn(msg):
    sys.stderr.write(f"  ! {msg}\n")


# ---------------------------------------------------------------- config.ini

def parse_config(path):
    """Возвращает {section: {'comment': str, 'keys': {k: v}}} в порядке файла."""
    sections = {}
    cur = None
    with open(path, encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                cur = line[1:-1].strip()
                sections[cur] = {"comment": [], "keys": {}}
            elif line.startswith(";") or line.startswith("#"):
                if cur is not None:
                    sections[cur]["comment"].append(line[1:].strip())
            elif "=" in line and cur is not None:
                k, v = line.split("=", 1)
                sections[cur]["keys"][k.strip()] = v.strip()
    for s in sections.values():
        s["comment"] = " ".join(c for c in s["comment"] if c)
    return sections


# ---------------------------------------------------------------- комментарий

def tokenize_comment(comment, loads, flags):
    """Разбирает комментарий слота на список нагрузок.

    Возвращает (items, module_badges), где item =
      {type, count, label: [..], flags: {..}, volt: str|None}
    Слова до первого типа достаются первому типу.
    """
    lower_loads = {k.lower(): k for k in loads}
    lower_flags = {k.lower(): k for k in flags}
    items, module_badges = [], []
    pending = {"label": [], "flags": {}, "notes": []}

    def target():
        return items[-1] if items else pending

    # текст в кавычках — назначение блока: уходит в примечание, а не в название
    quoted = []

    def stash(m):
        quoted.append((m.group(1) or m.group(2) or "").strip())
        return f" \x00{len(quoted) - 1}\x00 "

    comment = re.sub(r"'([^']*)'|\"([^\"]*)\"", stash, comment)
    # незакрытая кавычка — примечание до конца комментария
    comment = re.sub(r"'([^'\x00]*)$|\"([^\"\x00]*)$", stash, comment)

    for tok in re.split(r"[\s,]+", comment.strip()):
        if not tok:
            continue
        qm = re.fullmatch(r"\x00(\d+)\x00", tok)
        if qm:
            note = quoted[int(qm.group(1))]
            if note:
                target()["notes"].append(note)
            continue
        m = TYPE_RE.match(tok)
        if m and m.group(1).lower() in lower_loads:
            items.append({"type": lower_loads[m.group(1).lower()],
                          "count": int(m.group(2) or 1),
                          "label": [], "flags": {}, "notes": []})
            continue
        if tok.lower() in lower_flags:
            fname = lower_flags[tok.lower()]
            fdef = flags[fname] or {}
            if fdef.get("badge_on") == "module":
                if fdef.get("badge"):
                    module_badges.append(fdef["badge"])
            else:
                target()["flags"][fname] = fdef
            continue
        target()["label"].append(tok)

    if items and (pending["label"] or pending["flags"] or pending["notes"]):
        items[0]["label"] = pending["label"] + items[0]["label"]
        items[0]["flags"] = {**pending["flags"], **items[0]["flags"]}
        items[0]["notes"] = pending["notes"] + items[0]["notes"]
    for it in items:
        it["volt"] = None
        for tok in it["label"]:
            vm = VOLT_RE.match(tok)
            if vm:
                it["volt"] = vm.group(1).replace(",", ".") + "V"
    return items, module_badges, pending


# ---------------------------------------------------------------- сборка

def fmt_name(template, label, volt):
    s = template.replace("{label}", label or "").replace("{volt}", volt or "")
    lines = [ln.strip() for ln in s.split("\n")]
    return "\n".join(ln for ln in lines if ln)


class Builder:
    def __init__(self, db, vbus_volt=None):
        self.db = db
        self.vbus_volt = vbus_volt          # напряжение шины (из [SYSTEM]), для подписи DC-DC
        self.devices = []
        self.harnesses = []
        self.modules = []
        self.hid = 0
        # (slot, kind, index) -> device id: для подписей из crosslink
        self.channel_dev = {}
        self.dev_by_id = {}

    def next_h(self):
        self.hid += 1
        return self.hid

    def add_device(self, dev):
        self.devices.append(dev)
        self.dev_by_id[dev["id"]] = dev

    # ---- слот
    def build_slot(self, slot, mode, comment):
        modes = self.db["modes"]
        if mode not in modes:
            return None
        hw_name = modes[mode]["hw"]
        hw = self.db["hw_modules"][hw_name]
        items, badges, pending = tokenize_comment(comment, self.db["loads"],
                                                  self.db.get("flags", {}))
        if not items:
            items = [{"type": t, "count": 1, "label": [], "flags": {},
                      "notes": [], "volt": None}
                     for t in modes[mode].get("default", [])]
            # комментарий без типа (только подпись / примечание / флаги)
            # относится к первой нагрузке по умолчанию
            if items:
                items[0]["label"] = list(pending["label"])
                items[0]["flags"] = dict(pending["flags"])
                items[0]["notes"] = list(pending["notes"])
                for tok in pending["label"]:
                    vm = VOLT_RE.match(tok)
                    if vm:
                        items[0]["volt"] = vm.group(1).replace(",", ".") + "V"

        mod_id = f"s{slot}"
        module = {"id": mod_id, "name": hw_name, "slot": f"s_{slot}",
                  "pins": list(hw["pins"])}
        if mode != hw_name:
            module["mode"] = mode
        if badges:
            module["badges"] = badges
        self.modules.append(module)

        # очереди свободных каналов по видам
        free = {k: list(v) for k, v in hw.get("channels", {}).items()}
        used_idx = {k: 0 for k in free}

        # раскрываем _xN и считаем повторы ключей внутри слота
        instances = []
        for it in items:
            for _ in range(it["count"]):
                instances.append(it)
        key_counts = {}
        for it in instances:
            for d in self.db["loads"][it["type"]]["devices"]:
                key_counts[d["key"]] = key_counts.get(d["key"], 0) + 1
        key_seen = {}

        for it in instances:
            load = self.db["loads"][it["type"]]
            kind = load["channel"]
            if kind is None:                      # «none»: модуль без нагрузки
                continue
            need = int(load.get("channels", 1))
            if kind not in free or len(free[kind]) < need:
                warn(f"SLOT_{slot} ({hw_name}): нет свободных каналов '{kind}' "
                     f"для нагрузки {it['type']} — пропущена")
                continue
            chans = [free[kind].pop(0) for _ in range(need)]
            base_idx = used_idx[kind]
            used_idx[kind] += need

            volt = it["volt"] or load.get("volt_default")
            # если нагрузка использует {volt}, напряжение из подписи убираем —
            # оно уйдёт в имя БП, а не в подпись мотора
            uses_volt = any("{volt}" in d["name"] for d in load["devices"])
            label = " ".join(t for t in it["label"]
                             if not (uses_volt and VOLT_RE.match(t)))

            # канальные пометки (OC jumper) — у пинов занятых каналов
            for f in it["flags"].values():
                if f and f.get("badge_on") == "channel" and f.get("badge"):
                    pb = module.setdefault("pin_badges", {})
                    for ch in chans:
                        pb.setdefault(ch, []).append(f["badge"])

            # id устройств этой нагрузки
            ids = {}
            for d in load["devices"]:
                key_seen[d["key"]] = key_seen.get(d["key"], 0) + 1
                suffix = f"_{key_seen[d['key']]}" if key_counts[d["key"]] > 1 else ""
                ids[d["key"]] = f"{mod_id}_{d['key']}{suffix}"

            subst = {
                "{power}": hw.get("power"), "{gnd}": hw.get("gnd"),
                "{ch}": chans[0], "{contact}": "NC" if "NC" in it["flags"] else "NO",
            }
            for i, ch in enumerate(chans):
                subst[f"{{ch{i}}}"] = ch

            # DC-DC между модулем и нагрузкой — «насадка» на модуль: питание
            # нагрузки берётся с её выхода, сигнальные каналы проходят насквозь
            power_map = {}
            if "DCDC" in it["flags"]:
                out_v = it["volt"] or "?V"
                att = module.get("attachment")
                if not att:
                    in_v = self.vbus_volt or "Vbus"
                    # пины насадки повторяют пины слота один в один,
                    # только питание заменено на выход преобразователя
                    att_pins = [f"+{out_v}" if p == hw.get("power") else p
                                for p in hw["pins"]]
                    att = {"name": f"DC-DC\n{in_v} → {out_v}", "pins": att_pins}
                    module["attachment"] = att
                att_power = att["pins"][hw["pins"].index(hw["power"])]
                power_map = {"module:{power}": f"attach:{mod_id}:{att_power}",
                             "module:{gnd}":   f"attach:{mod_id}:{hw.get('gnd')}"}
                for ch in chans:
                    power_map[f"module:{ch}"] = f"attach:{mod_id}:{ch}"
                # насадка пропускает сквозь себя все сигнальные пины слота -
                # явные адреса module:<пин> из шаблона (Bt у buttonSmartLed
                # и т.п.) тоже уходят на её разъём, иначе жгут распадается
                for pin in att["pins"]:
                    if pin in hw["pins"]:
                        power_map.setdefault(f"module:{pin}", f"attach:{mod_id}:{pin}")

            # бейджи флагов — на основном блоке нагрузки (последнем в списке)
            dev_badges = [f["badge"] for f in it["flags"].values()
                          if f and f.get("badge") and f.get("badge_on") == "device"]
            for d in load["devices"]:
                dev = {"id": ids[d["key"]], "name": fmt_name(d["name"], label, volt),
                       "pins": list(d["pins"])}
                if d is load["devices"][-1]:
                    if dev_badges:
                        dev["badges"] = list(dev_badges)
                    if it.get("notes"):
                        dev["notes"] = list(it["notes"])
                self.add_device(dev)
            # устройство «на канале» для подписей crosslink — последнее в
            # списке нагрузки (у stepper это мотор, у реле — нагрузка)
            main_dev = ids[load["devices"][-1]["key"]]
            for i in range(need):
                self.channel_dev[(slot, kind, base_idx + i)] = main_dev

            for h in load["harnesses"]:
                # проводка зависит от типа выхода модуля (push-pull / open drain)
                tmpl = h.get("wires_" + str(hw.get("out_kind", ""))) or h.get("wires")
                if tmpl is None:
                    warn(f"SLOT_{slot}: у нагрузки {it['type']} нет проводки для "
                         f"out_kind='{hw.get('out_kind')}' — жгут пропущен")
                    continue
                wires = self._wires(tmpl, subst, ids, mod_id, slot, power_map)
                lbl = h.get("label", it["type"])
                if wires:
                    self.harnesses.append({"id": self.next_h(),
                                           "label": f"{lbl} (s_{slot})",
                                           "wires": wires})
        return module

    def _wires(self, tmpl, subst, ids, mod_id, slot, power_map=None):
        out = []
        for w in tmpl:
            ends = []
            ok = True
            for end in (w["a"], w["b"]):
                if power_map and end in power_map:
                    ends.append(power_map[end])
                    continue
                if power_map and end.startswith("module:"):
                    # module:{ch0} / module:{ch} -> module:ch_0 -> через насадку
                    pin = end[len("module:"):]
                    for k, v in subst.items():
                        if pin == k:
                            pin = v
                    if f"module:{pin}" in power_map:
                        ends.append(power_map[f"module:{pin}"])
                        continue
                if end.startswith("dev:"):
                    _, key, pin = end.split(":", 2)
                    ends.append(f"device:{ids[key]}:{pin}")
                elif end.startswith("module:"):
                    pin = end[len("module:"):]
                    for k, v in subst.items():
                        if pin == k:
                            pin = v
                    if pin is None or pin.startswith("{"):
                        warn(f"SLOT_{slot}: у модуля нет пина для '{end}' — провод пропущен")
                        ok = False
                        break
                    ends.append(f"module:{mod_id}:{pin}")
                else:
                    ends.append(end)
            if ok:
                out.append({"a": ends[0], "b": ends[1], "color": w.get("color", "black")})
        return out

    # ---- подписи из crosslink
    def apply_crosslinks(self, slots):
        for slot, sec in slots.items():
            cl = sec["keys"].get("crosslink", "")
            if not cl or cl.strip().lower() == "empty":
                continue
            for link in cl.split(","):
                if "->" not in link:
                    continue
                src, dst = (p.strip() for p in link.split("->", 1))
                ms, md = TOPIC_RE.match(src), TOPIC_RE.match(dst)
                if not ms or not md:
                    continue
                s_slot, ev = int(ms.group(2)), ms.group(4)
                d_mod, d_slot, act = md.group(1), int(md.group(2)), md.group(4)
                if s_slot == d_slot:
                    continue        # внутренняя связь слота (stepper -> stepper)
                idx = 0
                mch = re.match(r"^ch_(\d+)$", ev)
                if mch:
                    idx = int(mch.group(1))
                elif ev != "val":
                    continue
                dev_id = self.channel_dev.get((s_slot, "in", idx))
                if not dev_id:
                    continue
                dst_name = f"{d_mod}_{d_slot}"
                note = ACTION_NOTES.get(act, "→ {dst}/" + act).format(dst=dst_name)
                dev = self.dev_by_id[dev_id]
                dev.setdefault("notes", [])
                if note not in dev["notes"]:
                    dev["notes"].append(note)


def build_scheme(cfg, db):
    sysm = cfg.get("SYSTEM", {"comment": "", "keys": {}})
    name = sysm["keys"].get("deviceName", "moduleBox")
    board = sysm["keys"].get("boardVersion")

    ctrl = {"name": name, "serial": ""}
    if board:
        ctrl["board"] = f"плата v{board}"

    # LAN
    lan = cfg.get("LAN", {"keys": {}})["keys"]
    connectors = []
    if lan.get("LAN_enable", "0") == "1":
        if lan.get("DHCP", "0") == "1":
            connectors.append({"name": "Ethernet", "label": "DHCP"})
        else:
            ip = lan.get("ipAdress") or lan.get("ipAddress") or "?"
            mask = lan.get("netMask", "")
            cidr = ""
            if mask:
                try:
                    cidr = "/" + str(sum(bin(int(o)).count("1") for o in mask.split(".")))
                except ValueError:
                    cidr = ""
            connectors.append({"name": "Ethernet", "label": ip + cidr})
    connectors.append("USB")
    ctrl["connectors"] = connectors

    # протокол: MQTT -> адрес брокера, второй строкой в блоке Ethernet
    mqtt = cfg.get("MQTT", {"keys": {}})["keys"]
    broker = mqtt.get("mqttBrokerAdress") or mqtt.get("mqttBrokerAddress")
    if broker and broker.lower() not in ("", "empty", "0"):
        port = mqtt.get("mqttBrokerPort") or mqtt.get("port")
        line = "MQTT · брокер " + broker + (f":{port}" if port else "")
        eth = next((c for c in connectors if isinstance(c, dict) and c["name"] == "Ethernet"), None)
        if eth is None:                       # LAN выключен — всё равно показать
            eth = {"name": "Ethernet", "label": ""}
            connectors.insert(0, eth)
        eth["extra"] = [line]

    # [SYSTEM]-комментарий: БП и монтажная плита
    notes = []
    volt = watt = None
    for tok in re.split(r"[\s,]+", sysm["comment"]):
        if not tok:
            continue
        if VOLT_RE.match(tok):
            volt = VOLT_RE.match(tok).group(1) + "V"
        elif re.match(r"^\d+\s*[wWвВт]+$", tok):
            watt = re.match(r"^(\d+)", tok).group(1) + "W"
        elif tok.lower() == "mountplate":
            notes.append("монтажная плита")
        else:
            notes.append(tok)
    if notes:
        ctrl["notes"] = notes

    b = Builder(db, volt)
    ctrl["modules"] = []
    ctrl["power_module"] = {"name": "Power", "pins": ["+", "-"]}

    if volt:
        psu_name = "Блок питания " + volt + (f" {watt}" if watt else "")
        ctrl["psu"] = {"name": psu_name, "pins": ["+" + volt.rstrip("V"), "gnd"]}
        b.harnesses.append({"id": b.next_h(), "label": "питание контроллера",
                            "wires": [{"a": f"psu:+{volt.rstrip('V')}", "b": "power:+", "color": "red"},
                                      {"a": "psu:gnd", "b": "power:-", "color": "black"}]})

    slots = {}
    for sec, data in cfg.items():
        m = re.match(r"^SLOT_(\d+)$", sec)
        if not m:
            continue
        slot = int(m.group(1))
        slots[slot] = data
        mode = data["keys"].get("mode", "").strip()
        if not mode or mode == "empty":
            continue
        module = b.build_slot(slot, mode, data["comment"])
        if module is None:
            if mode in db.get("virtual_modes", []):
                pass
            elif mode not in db["modes"]:
                warn(f"SLOT_{slot}: mode '{mode}' нет в базе (loads.yaml) — пропущен")
            continue
        ctrl["modules"].append(module)

    b.apply_crosslinks(slots)

    if len(ctrl["modules"]) > 6:
        warn(f"в контроллере {len(ctrl['modules'])} физических модулей (> 6)")

    scheme = {
        "title": f"{name} — схема подключения",
        "controller": ctrl,
        "devices": b.devices,
        "harnesses": b.harnesses,
    }
    return scheme


HEADER = """\
# Схема подключения контроллера — сгенерировано из config.ini
#
# Пересобрать SVG и PDF после правки этого файла (из корня репозитория):
#   python tools/scheme_gen/generate.py "<путь к этому файлу>" --pdf
# Весь конвейер для папки контроллера (config.ini -> YAML -> SVG -> PDF):
#   python tools/scheme_gen/build.py "<папка с этим файлом>"
# Пересоздать сам YAML из config.ini (ЗАТРЁТ ручные правки ниже):
#   python tools/scheme_gen/from_config.py "<папка>/config.ini" --force
#
# Правки руками (цвета проводов, артикулы БП, подписи) делаются здесь;
# повторная генерация из config.ini НЕ перезаписывает файл без --force.
#
# Адреса пинов: device:<id>:<pin> | module:<id>:<pin> | power:<pin> | psu:<pin>
# Цвет провода задаётся ОДИН раз -> совпадает с обоих концов жгута.

"""


class Dumper(yaml.SafeDumper):
    pass


def _str(dumper, s):
    if "\n" in s:
        return dumper.represent_scalar("tag:yaml.org,2002:str", s, style='"')
    return dumper.represent_scalar("tag:yaml.org,2002:str", s)


Dumper.add_representer(str, _str)


def dump_scheme(scheme):
    # жгуты и провода — компактно в одну строку
    class Flow(dict):
        pass

    def flow(d):
        return Flow(d)

    Dumper.add_representer(Flow, lambda d, v: d.represent_mapping(
        "tag:yaml.org,2002:map", v, flow_style=True))
    for h in scheme["harnesses"]:
        h["wires"] = [flow(w) for w in h["wires"]]
    for d in scheme["devices"]:
        d["pins"] = list(d["pins"])
    text = yaml.dump(scheme, Dumper=Dumper, allow_unicode=True, sort_keys=False,
                     width=120, default_flow_style=None)
    return HEADER + text


def main():
    for stream in (sys.stdout, sys.stderr):      # кириллица в консоли Windows
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="config.ini -> scheme.yaml")
    ap.add_argument("config", help="путь к config.ini контроллера")
    ap.add_argument("-o", "--out", help="выходной YAML (по умолчанию <deviceName>.scheme.yaml рядом)")
    ap.add_argument("--loads", default=LOADS_DEFAULT, help="база нагрузок (loads.yaml)")
    ap.add_argument("--force", action="store_true", help="перезаписать существующий YAML")
    args = ap.parse_args()

    with open(args.loads, encoding="utf-8") as f:
        db = yaml.safe_load(f)
    cfg = parse_config(args.config)
    scheme = build_scheme(cfg, db)

    out = args.out or os.path.join(os.path.dirname(os.path.abspath(args.config)),
                                   scheme["controller"]["name"] + ".scheme.yaml")
    if os.path.exists(out) and not args.force:
        sys.exit(f"Файл уже есть: {out}\n  (в нём могут быть ручные правки; "
                 f"чтобы перезаписать — --force)")
    with open(out, "w", encoding="utf-8") as f:
        f.write(dump_scheme(scheme))
    print(f"OK: {out}  (модулей: {len(scheme['controller']['modules'])}, "
          f"устройств: {len(scheme['devices'])}, жгутов: {len(scheme['harnesses'])})")


if __name__ == "__main__":
    main()
