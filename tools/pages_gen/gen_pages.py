# -*- coding: utf-8 -*-
"""Собирает страницы программных модулей вики из манифеста прошивки + авторской прозы.

Механические разделы (Топики / Опции / События / Команды) берутся из
manifest_all.json — они гарантированно совпадают с прошивкой.
Проза (описание, принцип работы, примеры) задаётся в pages_data.py.
"""
import json, io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = os.path.join(HERE, '..', '..', 'content')
MAN = json.load(io.open(os.path.join(HERE, 'manifest_all.json'), encoding='utf-8'))

TYPEMAP = {'flag': 'флаг', 'int': 'число(int)', 'float': 'число(float)',
           'string': 'строка', 'enum': 'строка(enum)', 'color': 'строка(RGB)'}

# Опции и команды, встречающиеся во многих модулях: описания в манифесте
# у них разнородные, поэтому приводим к единому виду централизованно.
COMMON_OPTION_TEXT = {
    'eventFilter': '*флаг*, подавляет короткое событие `press`, когда сработало длинное '
                   'или двойное нажатие. По умолчанию выключен — короткие события шлются всегда.',
    'disableOnStart': '*флаг*, стартовать в выключенном состоянии и ждать `action/enable` '
                      'со значением `1`. По умолчанию модуль активен сразу.',
    'periodicUpdate': '*флаг*, принудительно отправлять буфер ленты каждый цикл обновления, '
                      'даже если картинка не изменилась.',
    'filterK': '*число(float)*, коэффициент сглаживающего фильтра (скользящее среднее), '
               'от 0 до 1. Значение 1 отключает фильтр. По умолчанию 1.',
}

COMMON_COMMAND_TEXT = {
    'action/toggleLedState': 'Переключить состояние подсветки на противоположное',
    'action/setFadeTime': 'Время переходного процесса при изменении яркости, $мСек$',
    'action/enable': 'Включить (`1`) или выключить (`0`) модуль',
}


def norm(s):
    if not s:
        return ''
    s = s.replace('\\n', ' ').replace('\n', ' ').replace('\t', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s


TAIL_PATTERNS = [
    # «По умолчанию 0 (выключено).»
    re.compile(r'[\s,.;–-]*По умолчанию [^.()]*\([^)]*\)\.?\s*$'),
    # «По умолчанию 10, 1-4096» в конце — добавляем сами, единообразно.
    re.compile(r'[\s,.;–-]*По умолчанию[^.()]*\.?\s*$'),
    # «…, по умолчанию 100 мс» строчными в конце фразы
    re.compile(r'\s*,\s*по умолчанию[^.()]*\.?\s*$'),
    # хвост «Флаг.» / «Без параметров.» - тип уже указан отдельной колонкой
    re.compile(r'[\s.,;-]*(?:Флаг|Без параметров|Int32?|Float)\.?\s*$'),
    # голый диапазон «0-255.» / «Int32 -2147483648..2147483647»
    re.compile(r'[\s,.;–-]*(?:Int32?|Float|Целое)?\s*-?\d+\s*(?:\.\.|[-–])\s*-?\d+\s*(?:мс|ms|мС)?\.?\s*$'),
]


def clean_desc(s, lower=False):
    """Убирает из описания хвосты «По умолчанию …» и голые диапазоны —
    генератор добавляет их сам, в едином виде."""
    s = norm(s)
    changed = True
    while changed:
        changed = False
        for p in TAIL_PATTERNS:
            new = p.sub('', s)
            if new != s:
                s, changed = new, True
    s = s.rstrip(' ,.;-–')
    if s:
        s = (s[0].lower() if lower else s[0].upper()) + s[1:]
    return s


def range_of(text):
    """Достаёт диапазон значений из описания команды, чтобы положить его в payload."""
    m = re.search(r'(-?\d+)\s*(?:\.\.|[-–])\s*(-?\d+)', norm(text or ''))
    if m and int(m.group(2)) > int(m.group(1)):
        return '`%s`–`%s`' % (m.group(1), m.group(2))
    return None


def fmt_option(o, override=None):
    name = o.get('name')
    override = dict(COMMON_OPTION_TEXT, **(override or {}))
    if name in override:
        return '- **%s** — %s' % (name, override[name])
    vt = o.get('valueType')
    t = TYPEMAP.get(vt, vt)
    desc = clean_desc(o.get('description'), lower=True)
    tail = []
    if vt == 'enum':
        vals = [v for v in o.get('values', []) if v]
        tail.append('Значения: ' + ', '.join('`%s`' % v for v in vals) + '.')
    lo, hi = o.get('valueMin'), o.get('valueMax')
    if vt in ('int', 'float') and lo is not None and hi is not None and hi > lo:
        tail.append('Диапазон %s–%s.' % (lo, hi))
    if 'valueDefault' in o and vt != 'flag':
        tail.append('По умолчанию %s.' % o.get('valueDefault'))
    line = '- **%s** — *%s*, %s' % (name, t, desc)
    if not line.rstrip().endswith('.'):
        line += '.'
    if tail:
        line += ' ' + ' '.join(tail)
    return line


UNIT_HINT = {
    'ms': '$мСек$', 'mm': '$мм$', 'cm': '$см$', 'hz': '$Гц$', 'Hz': '$Гц$',
    'fps': '$Гц$', 'deg': '$град$', 'percent': '%', 'step': '$шаг$',
    'step/sek': '$шаг/сек$', 'step/sek^2': '$шаг/сек^2$', 's': '$сек$',
    'sek': '$сек$', 'bytes': 'байт', 'num': '', 'bool': '', 'state': '',
    'ratio': '', 'string': '', 'unit': '', '': '',
}

PAYLOAD_BY_TYPE = {
    'int': 'целое', 'float': 'дробное', 'string': 'строка',
    'ratio': '`0.0`–`1.0`', 'bool': '`0` / `1`',
}


def payload_for_report(r):
    vt = r.get('valueType')
    unit = r.get('unit') or ''
    if (r.get('topic') or '').endswith('enable'):
        return '`0` / `1`'
    if unit == 'bool' or unit == 'state':
        return '`0` / `1`'
    if vt == 'ratio':
        return '`0.0`–`1.0`'
    base = PAYLOAD_BY_TYPE.get(vt, vt or '—')
    hint = UNIT_HINT.get(unit, '')
    if hint:
        return '%s, %s' % (base, hint)
    return base


def payload_for_cmd(c):
    params = [norm(p) for p in c.get('parameters', [])]
    params = [p for p in params if p]
    if not params:
        return '—'
    if c.get('command', '').endswith('enable'):
        return '`0` / `1`'
    if params == ['int']:
        return range_of(c.get('description')) or 'целое'
    if params == ['float']:
        return 'дробное'
    if params == ['string']:
        return 'строка'
    if params == ['int', 'int', 'int']:
        return '`R G B`'
    if c.get('parametersType') == 'enum':
        return ', '.join('`%s`' % p for p in params)
    return ', '.join(params)


def base_topic(full):
    """deviceName/button_<n> -> button_<slot>"""
    if not full:
        return None
    t = full.split('/', 1)[-1]
    return t.replace('<n>', '<slot>')


def build(spec):
    m = MAN[spec['manifest']]
    mode = spec.get('mode', m.get('mode'))
    trig = spec.get('trigger', base_topic(m.get('trigger')))
    act = spec.get('action', base_topic(m.get('action')))
    out = []
    w = out.append

    # --- frontmatter ---
    w('---')
    w('title: %s' % spec.get('title', mode))
    w('draft: false')
    w('tags:')
    for t in spec.get('tags', []):
        w('  - %s' % t)
    w('---')

    # --- mode block ---
    slots = m.get('slots', '')
    slot_line = spec.get('slot_line')
    if not slot_line:
        if slots and slots != '0-9' and slots != '0-5':
            slot_line = '[SLOT_n] ;доступные слоты: %s' % slots
        else:
            slot_line = '[SLOT_n]'
    w('```ini')
    w(slot_line)
    w('mode = %s' % mode)
    w('```')
    w(spec['intro'])
    w('')

    # --- Совместимость ---
    w('## Совместимость')
    if spec.get('virtual'):
        w(spec.get('compat_text',
                   'Виртуальный модуль, аппаратной части не требует. '
                   'Доступные слоты: %s.' % slots))
    else:
        for link, label in spec.get('compat', []):
            w('- [[%s|%s]]' % (link, label))
        if spec.get('compat_note'):
            w('')
            w(spec['compat_note'])
    w('')

    # --- Принцип работы ---
    w('## Принцип работы')
    w(spec['principle'].strip())
    w('')

    # --- Топики ---
    w('## Топики')
    if trig:
        w('База топика события:')
        w('- `<deviceName>/%s` — например `moduleBox/%s`'
          % (trig, trig.replace('<slot>', '0')))
        w('')
    if act:
        w('База топика действия:')
        w('- `<deviceName>/%s` — например `moduleBox/%s`'
          % (act, act.replace('<slot>', '0')))
        w('')
    w('Полный топик — база плюс направление и имя: '
      '`moduleBox/%s`.' % spec['topic_example'])
    if spec.get('topic_note'):
        w('')
        w(spec['topic_note'])
    w('')

    # --- Опции ---
    opts = m.get('options', [])
    skip = set(spec.get('skip_options', []))
    override = spec.get('option_text', {})
    groups = spec.get('option_groups')
    seen = set()
    uniq = []
    for o in opts:
        n = o.get('name')
        if n in skip:
            continue
        if n in seen:
            continue
        seen.add(n)
        uniq.append(o)
    by_name = dict((o['name'], o) for o in uniq)

    w('## Опции')
    if groups:
        for gtitle, names in groups:
            w(gtitle)
            for n in names:
                if n in by_name:
                    w(fmt_option(by_name[n], override))
                elif n in override:
                    w('- **%s** — %s' % (n, override[n]))
                else:
                    raise SystemExit('!! %s: нет опции %s в манифесте' % (mode, n))
            w('')
        listed = set(n for _, ns in groups for n in ns)
        rest = [o for o in uniq if o['name'] not in listed]
        if rest:
            raise SystemExit('!! %s: опции вне групп: %s'
                             % (mode, [o['name'] for o in rest]))
    else:
        if uniq:
            w('Доступные опции:')
            for o in uniq:
                w(fmt_option(o, override))
        else:
            w('Модуль дополнительных опций не имеет.')
        w('')
    for extra in spec.get('extra_options', []):
        w(extra)
    if spec.get('extra_options'):
        w('')

    # --- События ---
    reps = [r for r in m.get('reports', []) if r.get('topic') not in spec.get('skip_reports', [])]
    if reps:
        w('## События')
        w('| Топик | Payload | Описание |')
        w('|---|---|---|')
        base = trig or act
        for r in reps:
            topic = r.get('topic')
            desc = spec.get('report_text', {}).get(topic) or clean_desc(r.get('description'))
            desc = desc.rstrip('.')
            pl = spec.get('report_payload', {}).get(topic) or payload_for_report(r)
            w('| `%s/%s` | %s | %s |' % (base, topic, pl, desc))
        w('')
        if spec.get('report_example'):
            w(spec['report_example'])
            w('')

    # --- Команды ---
    cmds = [c for c in m.get('commands', []) if c.get('command') not in spec.get('skip_commands', [])]
    if cmds:
        # action/enable — всегда последней строкой
        cmds = ([c for c in cmds if c.get('command') != 'action/enable'] +
                [c for c in cmds if c.get('command') == 'action/enable'])
        w('## Команды')
        w('| Топик | Payload | Описание |')
        w('|---|---|---|')
        base = act or trig
        cmd_text = dict(COMMON_COMMAND_TEXT, **spec.get('command_text', {}))
        for c in cmds:
            name = c.get('command')
            desc = cmd_text.get(name) or clean_desc(c.get('description'))
            desc = desc.rstrip('.')
            pl = spec.get('command_payload', {}).get(name) or payload_for_cmd(c)
            w('| `%s/%s` | %s | %s |' % (base, name, pl, desc))
        w('')
        if spec.get('command_example'):
            w(spec['command_example'])
            w('')

    # --- дополнительные разделы ---
    for title, body in spec.get('sections', []):
        w('## %s' % title)
        w(body.strip())
        w('')

    # --- Примеры ---
    w('## Примеры')
    w(spec['examples'].strip())
    w('')
    w('Подробнее — [[Платформа moduleBox/CrossLink|внутренние связи (crossLink)]].')

    if spec.get('scheme'):
        w('')
        w('## Пример подключения')
        w('![[%s]]' % spec['scheme'])

    text = '\n'.join(out)
    text = re.sub(r'\n{3,}', '\n\n', text) + '\n'
    return text


def write_pages(specs):
    n = 0
    for spec in specs:
        path = os.path.join(WIKI, spec['path'])
        text = build(spec)
        d = os.path.dirname(path)
        if not os.path.isdir(d):
            os.makedirs(d)
        io.open(path, 'w', encoding='utf-8', newline='\n').write(text)
        print('  ok', spec['path'])
        n += 1
    print('written:', n)


if __name__ == '__main__':
    import pages_data
    write_pages(pages_data.SPECS)
