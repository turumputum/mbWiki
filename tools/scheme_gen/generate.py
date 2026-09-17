# -*- coding: utf-8 -*-
"""
Генератор схем подключения moduleBox.

Вход : YAML-описание схемы (см. tools/scheme_gen/README.md и *.scheme.yaml).
Выход: SVG с фиксированной раскладкой.

Раскладка (одинаковая для всех схем):
  - Контроллер  -> справа: шапка (имя + пустой блок под серийный номер),
    разъёмы Ethernet/USB, модули (1..6), модуль питания всегда внизу.
  - ПК-сервер   -> опционально над контроллером.
  - Блок питания-> опционально под контроллером.
  - Устройства  -> слева (драйверы, нагрузки, датчики), пины подписаны.
  - Жгуты       -> пронумерованы, в среднем поле; цветные провода идут
    от пина к пину. Цвет провода задаётся один раз -> совпадает с обоих концов.

Запуск:
  python tools/scheme_gen/generate.py <scheme.yaml> [-o out.svg]
"""

import sys
import os
import argparse
import html

try:
    import yaml
except ImportError:
    sys.exit("Нужен PyYAML:  python -m pip install pyyaml")

# ---------------------------------------------------------------- константы

COL_W      = 300      # ширина блока (устройство / модуль)
ROW_H      = 26       # высота строки пина
HEADER_H   = 51       # высота шапки
GAP_V      = 22       # вертикальный зазор между блоками
SLOT_W     = 22       # полоса с номером слота справа от модуля
PIN_COL_W  = 84       # ширина колонки пинов внутри блока
STUB       = 16       # длина горизонтального «выхода» провода из пина
MARGIN     = 36       # поля холста
ATT_W      = 136      # ширина «насадки» на модуль (DC-DC и т.п.), слева от модуля
ATT_PIN_W  = 70       # колонка пинов насадки (номер + имя, как у модуля)

# горизонтальные зоны
LEFT_X     = MARGIN                       # левый край устройств
MID_X      = LEFT_X + COL_W               # начало среднего поля (жгуты)
MID_W      = 560                          # ширина среднего поля
CTRL_X     = MID_X + MID_W                # левый край контроллера

# именованные цвета проводов -> hex
WIRE_COLORS = {
    "red":    "#e23b3b",
    "black":  "#3a3a3a",
    "blue":   "#2f6fdb",
    "green":  "#2ca02c",
    "yellow": "#e6b400",
    "orange": "#e8730c",
    "white":  "#9aa0a6",
    "gray":   "#9aa0a6",
    "brown":  "#8a5a2b",
    "violet": "#8b4fc4",
}

# палитра оформления
C_BOX      = "#ffffff"
C_STROKE   = "#4a4a4a"
C_HEADER   = "#eef2f6"
C_MODULE   = "#f6f8fa"
C_PIN      = "#fbfcfd"
C_TEXT     = "#1f2328"
C_MUTED    = "#5b6571"
FONT       = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"


def esc(s):
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- SVG-хелперы

class SVG:
    def __init__(self):
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill=C_BOX, stroke=C_STROKE, rx=6, sw=1.4):
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                 f'rx="{rx}" ry="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def line(self, x1, y1, x2, y2, stroke=C_STROKE, sw=1):
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, s, size=13, anchor="start", fill=C_TEXT,
             weight="normal", rotate=None):
        tr = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" '
                 f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
                 f'text-anchor="{anchor}"{tr}>{esc(s)}</text>')

    def polyline(self, pts, stroke, sw=2.4):
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.add(f'<polyline points="{d}" fill="none" stroke="{stroke}" '
                 f'stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>')

    def dot(self, x, y, r, fill, stroke="#ffffff", sw=1):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{sw}"/>')

    def dump(self, w, h):
        body = "\n".join(self.parts)
        return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
                f'viewBox="0 0 {w} {h}">\n'
                f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
                f'{body}\n</svg>\n')


def multiline(s):
    """Разбивает строку по \\n на список строк."""
    return str(s).split("\n")


def conn_parts(c):
    """Разъём: строка или {name, label} -> (name, label)."""
    if isinstance(c, dict):
        return c.get("name", ""), c.get("label", "")
    return str(c), ""


def conn_extra(c):
    """Дополнительные строки разъёма (протокол, брокер...) — list[str]."""
    if isinstance(c, dict):
        ex = c.get("extra") or []
        return [ex] if isinstance(ex, str) else [str(e) for e in ex]
    return []


def conn_h(c):
    """Высота строки разъёма: базовая + по 15 px на каждую доп. строку."""
    return ROW_H + 15 * len(conn_extra(c))


def module_key(m):
    """Ключ модуля для адресации пинов: id, если задан, иначе name."""
    return m.get("id") or m["name"]


def unique_pins(pins):
    """Повторяющиеся имена пинов -> 'COM', 'COM.2', 'COM.3' для адресации."""
    seen, out = {}, []
    for p in pins:
        seen[p] = seen.get(p, 0) + 1
        out.append(p if seen[p] == 1 else f"{p}.{seen[p]}")
    return out


def device_header_lines(d):
    """Строки шапки устройства: имя (\\n) + примечания (`notes:` или `note:`)."""
    notes = d.get("notes") or d.get("note") or []
    if isinstance(notes, str):
        notes = [notes]
    return multiline(d["name"]), [str(n) for n in notes]


def device_header_h(d):
    names, notes = device_header_lines(d)
    h = 10 + 13 * len(names) + 12 * len(notes) + 8
    return max(HEADER_H, h)


# ---------------------------------------------------------------- раскладка

class Layout:
    """Считает геометрию блоков и регистрирует якоря пинов."""

    def __init__(self, scheme):
        self.scheme = scheme
        self.anchors = {}     # endpoint-key -> (x, y, dir)   dir: +1 вправо, -1 влево
        self.boxes = []       # отрисовочные задания

    # --- регистрация якоря пина:  (x, y, dir, group)
    def _anchor(self, key, x, y, direction, group):
        self.anchors[key] = (x, y, direction, group)

    def build(self):
        s = self.scheme
        # ---- правый стек: server? -> controller -> psu?
        right_h = self._measure_right()
        # ---- левый стек: устройства
        left_h = self._measure_left()

        self.canvas_h = max(right_h, left_h) + 2 * MARGIN
        self.canvas_w = CTRL_X + COL_W + SLOT_W + MARGIN
        # есть ли «насадки» на модулях — тогда жгуты не заходят под них
        self.att_w = ATT_W if any(m.get("attachment")
                                  for m in s["controller"].get("modules", [])) else 0

        self._place_right()
        self._place_left()

    # ---- измерения высоты
    def _ctrl_height(self):
        c = self.scheme["controller"]
        h = HEADER_H
        h += sum(conn_h(cn) for cn in c.get("connectors", ["Ethernet", "USB"]))
        for m in c.get("modules", []):
            h += self._module_h(m)
        h += self._module_h(c["power_module"])
        return h

    def _module_h(self, m):
        h = max(len(m["pins"]) * ROW_H + 8, 64)
        extra = (14 if m.get("mode") else 0) + (20 if m.get("badges") else 0)
        att = m.get("attachment")
        if att:
            h = max(h, len(att["pins"]) * ROW_H + 8)
        return max(h, 44 + extra)

    def _measure_right(self):
        h = 0
        if self.scheme["controller"].get("server"):
            h += 50 + GAP_V
        h += self._ctrl_height()
        if self.scheme["controller"].get("psu"):
            psu = self.scheme["controller"]["psu"]
            h += GAP_V + HEADER_H + len(psu["pins"]) * ROW_H + 8
        return h

    def _device_h(self, d):
        return device_header_h(d) + len(d["pins"]) * ROW_H + 8

    def _measure_left(self):
        h = 0
        for d in self.scheme.get("devices", []):
            h += self._device_h(d) + GAP_V
        return h - GAP_V if h else 0

    # ---- размещение правого стека
    def _place_right(self):
        c = self.scheme["controller"]
        y = MARGIN
        if c.get("server"):
            self.boxes.append(("server", CTRL_X, y, c["server"]))
            y += 50 + GAP_V

        self.ctrl_top = y
        # шапка
        self.boxes.append(("ctrl_header", CTRL_X, y, c))
        y += HEADER_H
        # разъёмы
        for name in c.get("connectors", ["Ethernet", "USB"]):
            self.boxes.append(("connector", CTRL_X, y, name))
            y += conn_h(name)
        # модули
        for m in c.get("modules", []):
            mh = self._module_h(m)
            self.boxes.append(("module", CTRL_X, y, m, mh))
            self._register_module_pins(m, CTRL_X, y, mh)
            att = m.get("attachment")
            if att:
                # насадка: прижата к модулю слева, пины наружу (влево)
                ax = CTRL_X - ATT_W
                self.boxes.append(("attachment", ax, y, att, mh))
                top = y + (mh - len(att["pins"]) * ROW_H) / 2
                key = module_key(m)
                for i, pin in enumerate(unique_pins(att["pins"])):
                    self._anchor(f'attach:{key}:{pin}', ax, top + (i + 0.5) * ROW_H,
                                 -1, f'att:{key}')
            y += mh
        # модуль питания
        pm = c["power_module"]
        pmh = self._module_h(pm)
        self.boxes.append(("module", CTRL_X, y, pm, pmh))
        self._register_module_pins(pm, CTRL_X, y, pmh, is_power=True)
        y += pmh
        self.ctrl_bottom = y

        # блок питания под контроллером
        if c.get("psu"):
            psu = c["psu"]
            y += GAP_V
            ph = HEADER_H + len(psu["pins"]) * ROW_H + 8
            self.boxes.append(("psu", CTRL_X, y, psu, ph))
            self._register_psu_pins(psu, CTRL_X, y)

    def _register_module_pins(self, m, x, y, h, is_power=False):
        # пины модуля -> якорь на ЛЕВОЙ грани, провод уходит влево (dir -1)
        top = y + (h - len(m["pins"]) * ROW_H) / 2
        prefix = "power" if is_power else f'module:{module_key(m)}'
        group = "power" if is_power else f'mod:{module_key(m)}'
        for i, pin in enumerate(unique_pins(m["pins"])):
            py = top + (i + 0.5) * ROW_H
            self._anchor(f'{prefix}:{pin}', x, py, -1, group)

    def _register_psu_pins(self, psu, x, y):
        top = y + HEADER_H
        for i, pin in enumerate(psu["pins"]):
            py = top + (i + 0.5) * ROW_H
            self._anchor(f'psu:{pin}', x, py, -1, "psu")

    # ---- размещение левого стека
    def _place_left(self):
        y = MARGIN
        for d in self.scheme.get("devices", []):
            dh = self._device_h(d)
            self.boxes.append(("device", LEFT_X, y, d, dh))
            top = y + device_header_h(d)
            for i, pin in enumerate(unique_pins(d["pins"])):
                py = top + (i + 0.5) * ROW_H
                # пины устройства -> якорь на ПРАВОЙ грани, провод уходит вправо
                self._anchor(f'device:{d["id"]}:{pin}', LEFT_X + COL_W, py, +1,
                             f'dev:{d["id"]}')
            y += dh + GAP_V


# ---------------------------------------------------------------- отрисовка

def draw_box_header(svg, x, y, w, h, title, fill=C_HEADER):
    svg.rect(x, y, w, h, fill=fill)
    ty = y + 17                          # надпись прижата к верху
    for ln in multiline(title):
        svg.text(x + 12, ty, ln, size=13, weight="bold")
        ty += 14


def draw_badges(svg, x, y, badges, anchor="start"):
    """Ряд «пилюль» с пометками (OC jumper, NPN ...). y — базовая линия текста."""
    bx = x
    for b in badges:
        w = 7 * len(str(b)) + 14
        rx = bx if anchor == "start" else bx - w
        svg.rect(rx, y - 11, w, 16, fill="#fff4d6", stroke="#d19a00", rx=8, sw=1)
        svg.text(rx + w / 2, y + 1, b, size=10, anchor="middle", fill="#6b4e00",
                 weight="bold")
        bx += (w + 6) if anchor == "start" else -(w + 6)


def draw_device(svg, x, y, d, h):
    svg.rect(x, y, COL_W, h)
    hh = device_header_h(d)
    # шапка: заголовок слева + блок справа (бейджи)
    hdr_left = COL_W - PIN_COL_W
    svg.rect(x, y, hdr_left, hh, fill=C_HEADER, rx=6)
    svg.rect(x + hdr_left, y, PIN_COL_W, hh, fill=C_BOX, rx=6)
    names, notes = device_header_lines(d)
    ty = y + 16                          # надпись прижата к верху
    for ln in names:
        svg.text(x + 10, ty, ln, size=12, weight="bold")
        ty += 13
    for ln in notes:
        svg.text(x + 10, ty, ln, size=11, fill=C_MUTED)
        ty += 12
    if d.get("badges"):
        draw_badges(svg, x + COL_W - 8, y + 16, d["badges"], anchor="end")
    # колонка пинов справа
    pin_x = x + COL_W - PIN_COL_W
    svg.line(pin_x, y + hh, pin_x, y + h)
    top = y + hh
    for i, pin in enumerate(d["pins"]):
        py = top + i * ROW_H
        if i:
            svg.line(pin_x, py, x + COL_W, py, stroke="#d7dce1")
        svg.text(x + COL_W - 12, py + ROW_H / 2 + 4, pin, size=12, anchor="end")


def draw_module(svg, x, y, m, h, is_power=False):
    fill = C_MODULE if not is_power else "#f0efe6"
    svg.rect(x, y, COL_W, h, fill=fill, rx=0)
    # колонка пинов слева
    svg.line(x + PIN_COL_W, y, x + PIN_COL_W, y + h)
    top = y + (h - len(m["pins"]) * ROW_H) / 2
    npins = len(m["pins"])
    for i, pin in enumerate(m["pins"]):
        py = top + i * ROW_H
        if i:
            svg.line(x, py, x + PIN_COL_W, py, stroke="#d7dce1")
        # нумерация снизу вверх: нижний пин = 0
        svg.text(x + 10, py + ROW_H / 2 + 4, str(npins - 1 - i), size=11,
                 weight="bold", fill=C_MUTED)
        svg.text(x + 28, py + ROW_H / 2 + 4, pin, size=12)
        # канальные пометки (OC jumper и т.п.) — пилюля у пина, в теле модуля
        pb = (m.get("pin_badges") or {}).get(pin)
        if pb:
            draw_badges(svg, x + PIN_COL_W + 6, py + ROW_H / 2 + 3, pb)
    # имя модуля по центру тела (+ mode и бейджи под ним)
    body_cx = x + PIN_COL_W + (COL_W - PIN_COL_W - SLOT_W) / 2
    lines = 1 + (1 if m.get("mode") else 0) + (1 if m.get("badges") else 0)
    ty = y + h / 2 + 4 - (lines - 1) * 8
    svg.text(body_cx, ty, m["name"], size=13, weight="bold", anchor="middle")
    if m.get("mode"):
        ty += 15
        svg.text(body_cx, ty, f'mode: {m["mode"]}', size=11, anchor="middle",
                 fill=C_MUTED)
    if m.get("badges"):
        ty += 18
        total = sum(7 * len(str(b)) + 14 for b in m["badges"]) + 6 * (len(m["badges"]) - 1)
        draw_badges(svg, body_cx - total / 2, ty, m["badges"])
    # полоса слота справа
    slot = m.get("slot")
    if slot:
        sx = x + COL_W - SLOT_W
        svg.rect(sx, y, SLOT_W, h, fill="#e7ebef", rx=0)
        svg.text(sx + SLOT_W / 2 + 4, y + h / 2, slot, size=11,
                 anchor="middle", fill=C_MUTED, rotate=-90)


def draw_attachment(svg, x, y, att, h):
    """«Насадка» на модуль (DC-DC и т.п.): колонка пинов как у модуля, имя справа."""
    svg.rect(x, y, ATT_W, h, fill="#fff7e6", rx=0)
    pin_w = ATT_PIN_W
    svg.line(x + pin_w, y, x + pin_w, y + h)
    top = y + (h - len(att["pins"]) * ROW_H) / 2
    npins = len(att["pins"])
    for i, pin in enumerate(att["pins"]):
        py = top + i * ROW_H
        if i:
            svg.line(x, py, x + pin_w, py, stroke="#e6d9bd")
        # нумерация снизу вверх, как у модуля
        svg.text(x + 8, py + ROW_H / 2 + 4, str(npins - 1 - i), size=11,
                 weight="bold", fill=C_MUTED)
        svg.text(x + 24, py + ROW_H / 2 + 4, pin, size=12)
    lines = multiline(att["name"])
    cx = x + pin_w + (ATT_W - pin_w) / 2
    ty = y + h / 2 + 4 - (len(lines) - 1) * 6.5
    for ln in lines:
        svg.text(cx, ty, ln, size=10, weight="bold", anchor="middle", fill="#6b4e00")
        ty += 13


def draw_connector(svg, x, y, conn):
    name, label = conn_parts(conn)
    extra = conn_extra(conn)
    h = conn_h(conn)
    svg.rect(x, y, COL_W, h, fill=C_BOX, rx=0)
    # глиф порта
    svg.rect(x + 12, y + 6, 20, ROW_H - 12, fill="#dfe4e9", stroke=C_MUTED, rx=2, sw=1)
    svg.text(x + 42, y + ROW_H / 2 + 4, name, size=12, weight="bold")
    if label:
        svg.text(x + COL_W - 12, y + ROW_H / 2 + 4, label, size=11, anchor="end",
                 fill=C_MUTED)
    # дополнительные строки (протокол, брокер) — прижаты вправо
    ty = y + ROW_H + 8
    for ln in extra:
        svg.text(x + COL_W - 12, ty, ln, size=11, anchor="end", fill=C_MUTED)
        ty += 15


def draw_server(svg, x, y, label):
    name = label if isinstance(label, str) else "ПК / сервер"
    svg.rect(x, y, COL_W, 50)
    svg.text(x + COL_W / 2, y + 50 / 2 + 4, name, size=13,
             weight="bold", anchor="middle")


def render_boxes(svg, layout):
    for box in layout.boxes:
        kind = box[0]
        if kind == "server":
            draw_server(svg, box[1], box[2], box[3])
        elif kind == "ctrl_header":
            x, y, c = box[1], box[2], box[3]
            mid = COL_W / 2
            svg.rect(x, y, COL_W, HEADER_H, fill=C_HEADER)
            svg.line(x + mid, y, x + mid, y + HEADER_H, stroke=C_STROKE)
            svg.text(x + 12, y + 19, c["name"], size=14, weight="bold")
            if c.get("board"):
                svg.text(x + 12, y + 36, c["board"], size=11, fill=C_MUTED)
            serial = c.get("serial", "")
            if serial:
                svg.text(x + mid + COL_W / 4, y + 18,
                         serial, size=10, anchor="middle", fill=C_MUTED)
            ny = y + 18 if not serial else y + 33
            for n in c.get("notes", []):
                svg.text(x + mid + COL_W / 4, ny, n, size=10, anchor="middle",
                         fill=C_MUTED)
                ny += 12
        elif kind == "connector":
            draw_connector(svg, box[1], box[2], box[3])
        elif kind == "attachment":
            draw_attachment(svg, box[1], box[2], box[3], box[4])
        elif kind == "module":
            m = box[3]
            is_power = m is layout.scheme["controller"]["power_module"]
            draw_module(svg, box[1], box[2], m, box[4], is_power)
        elif kind == "psu":
            x, y, psu, h = box[1], box[2], box[3], box[4]
            svg.rect(x, y, COL_W, h)
            draw_box_header(svg, x, y, COL_W, HEADER_H, psu["name"])
            top = y + HEADER_H
            # колонка пинов слева — со стороны проводов
            pin_x = x + PIN_COL_W
            svg.line(pin_x, top, pin_x, y + h)
            for i, pin in enumerate(psu["pins"]):
                py = top + i * ROW_H
                if i:
                    svg.line(x, py, pin_x, py, stroke="#d7dce1")
                svg.text(x + 12, py + ROW_H / 2 + 4, pin, size=12)
        elif kind == "device":
            draw_device(svg, box[1], box[2], box[3], box[4])


# ---------------------------------------------------------------- жгуты

FAN        = 32       # отступ точки сбора жгута от грани блока
TRUNK_W    = 7        # толщина линии жгута
TRUNK_COL  = "#7b8794"


def _resolve(layout, h):
    """Разбирает провода жгута: список (a, b, color) и группы пинов по блокам."""
    wires, groups = [], {}
    for w in h.get("wires", []):
        a = layout.anchors.get(w["a"])
        b = layout.anchors.get(w["b"])
        if not a or not b:
            miss = w["a"] if not a else w["b"]
            sys.stderr.write(f"  ! жгут {h['id']}: не найден пин '{miss}'\n")
            continue
        color = WIRE_COLORS.get(w.get("color", "black"), w.get("color", "#3a3a3a"))
        wires.append((a, b, color))
        for ep in (a, b):
            groups.setdefault(ep[3], []).append(ep)
    return wires, groups


def _harness_geometry(layout, harnesses):
    """Классифицирует жгуты и назначает каждому канал cx."""
    info = []
    for h in harnesses:
        wires, groups = _resolve(layout, h)
        eps = [e for g in groups.values() for e in g]
        dirs = {e[2] for e in eps}
        avg = sum(e[1] for e in eps) / len(eps) if eps else 0
        if dirs == {+1}:
            kind = "left"            # устройство <-> устройство
        elif dirs == {-1}:
            kind = "right"           # контроллер <-> блок питания
        else:
            kind = "cross"           # устройство <-> модуль
        info.append(dict(h=h, wires=wires, groups=groups, kind=kind, avg=avg))

    left  = [i for i in info if i["kind"] == "left"]
    right = [i for i in info if i["kind"] == "right"]
    cross = sorted([i for i in info if i["kind"] == "cross"], key=lambda i: i["avg"])
    for n, i in enumerate(left):
        i["cx"] = MID_X + 60 + n * 34
    for n, i in enumerate(right):
        i["cx"] = CTRL_X - 60 - n * 34
    span0 = MID_X + 60 + len(left) * 34 + 50
    span1 = CTRL_X - layout.att_w - 60 - len(right) * 34 - 50
    step = (span1 - span0) / max(len(cross), 1)
    for n, i in enumerate(cross):
        i["cx"] = span0 + step * (n + 0.5)
    return info


def render_harnesses(svg, layout):
    info = _harness_geometry(layout, layout.scheme.get("harnesses", []))

    for inf in info:
        h, cx = inf["h"], inf["cx"]
        wires, groups = inf["wires"], inf["groups"]
        if not wires:
            continue

        if len(groups) == 2:
            # точка сбора у каждого блока: на отступе FAN от грани
            cps = {}
            for gk, eps in groups.items():
                ex, ed = eps[0][0], eps[0][2]
                ey = sum(e[1] for e in eps) / len(eps)
                cps[gk] = (ex + ed * (STUB + FAN), ey)
            (caX, caY), (cbX, cbY) = cps[list(groups)[0]], cps[list(groups)[1]]

            # толстая линия жгута между точками сбора
            svg.polyline([(caX, caY), (cx, caY), (cx, cbY), (cbX, cbY)],
                         TRUNK_COL, sw=TRUNK_W)
            # цветные «хвосты» проводов от пинов к точкам сбора
            for a, b, color in wires:
                for ep in (a, b):
                    ex, ey, ed, gk = ep
                    cpx, cpy = cps[gk]
                    svg.polyline([(ex, ey), (ex + ed * STUB, ey), (cpx, cpy)],
                                 color, sw=2.6)
                    svg.dot(ex, ey, 3.6, color)
            node_y = (caY + cbY) / 2
        else:
            # запасной режим: тонкие провода по каналу
            ys = []
            for a, b, color in wires:
                ax, ay, ad, _ = a
                bx, by, bd, _ = b
                svg.polyline([(ax, ay), (ax + ad * STUB, ay), (cx, ay),
                              (cx, by), (bx + bd * STUB, by), (bx, by)], color)
                svg.dot(ax, ay, 3.6, color)
                svg.dot(bx, by, 3.6, color)
                ys += [ay, by]
            node_y = (min(ys) + max(ys)) / 2

        # номерная метка жгута на линии
        svg.add(f'<circle cx="{cx:.1f}" cy="{node_y:.1f}" r="12.5" '
                f'fill="#ffffff" stroke="#222" stroke-width="1.7"/>')
        svg.text(cx, node_y + 4.5, h["id"], size=13, weight="bold", anchor="middle")


# ---------------------------------------------------------------- main

def export_pdf(svg_path, pdf_path):
    """SVG -> PDF через Inkscape (должен быть в PATH или в стандартной папке)."""
    import shutil
    import subprocess
    exe = shutil.which("inkscape")
    if not exe and os.name == "nt":
        for cand in (r"C:\Program Files\Inkscape\bin\inkscape.exe",
                     r"C:\Program Files\Inkscape\bin\inkscape.com"):
            if os.path.exists(cand):
                exe = cand
                break
    if not exe:
        sys.stderr.write("  ! Inkscape не найден — PDF не создан\n")
        return False
    subprocess.run([exe, svg_path, "--export-type=pdf",
                    f"--export-filename={pdf_path}"], check=True)
    print(f"OK: {pdf_path}")
    return True


def generate(scheme_path, out_path):
    with open(scheme_path, encoding="utf-8") as f:
        scheme = yaml.safe_load(f)

    layout = Layout(scheme)
    layout.build()

    svg = SVG()
    if scheme.get("title"):
        svg.text(MARGIN, MARGIN - 12, scheme["title"], size=16, weight="bold")
    render_harnesses(svg, layout)   # провода под блоками
    render_boxes(svg, layout)

    # легенда жгутов
    labelled = [h for h in scheme.get("harnesses", []) if h.get("label")]
    legend_h = 0
    if labelled:
        ly = layout.canvas_h + 6
        svg.text(MARGIN, ly + 4, "Жгуты:", size=12, weight="bold")
        lx = MARGIN + 64
        for h in labelled:
            svg.add(f'<circle cx="{lx + 9:.1f}" cy="{ly:.1f}" r="9" '
                    f'fill="#ffffff" stroke="#222" stroke-width="1.5"/>')
            svg.text(lx + 9, ly + 4, h["id"], size=11, weight="bold", anchor="middle")
            svg.text(lx + 24, ly + 4, h["label"], size=11, fill=C_MUTED)
            lx += 24 + 7.2 * len(str(h["label"])) + 26
            if lx > layout.canvas_w - 200:
                lx = MARGIN + 64
                ly += 24
        legend_h = ly - layout.canvas_h + 20

    out = svg.dump(layout.canvas_w, layout.canvas_h + legend_h)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"OK: {out_path}  ({layout.canvas_w}x{layout.canvas_h})")


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):     # кириллица в консоли Windows
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Генератор схем подключения moduleBox")
    ap.add_argument("scheme", help="путь к YAML-описанию схемы")
    ap.add_argument("-o", "--out", help="путь к выходному SVG")
    ap.add_argument("--pdf", action="store_true", help="дополнительно сохранить PDF (Inkscape)")
    args = ap.parse_args()

    out = args.out
    if not out:
        base = os.path.splitext(args.scheme)[0]
        if base.endswith(".scheme"):
            base = base[:-7]
        out = base + ".svg"
    generate(args.scheme, out)
    if args.pdf:
        export_pdf(out, os.path.splitext(out)[0] + ".pdf")
