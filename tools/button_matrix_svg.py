"""Принципиальная схема матрицы кнопок для страницы buttonMatrix.

    python tools/button_matrix_svg.py   # -> content/Программные модули/_assets/buttonMatrix.svg

3 строки (3n_mosfet, outSlots) x 3 столбца (in_3ch, inSlots); в каждой клетке
нормально разомкнутый контакт между строкой и столбцом. Символ клетки - из
mapping построчно.
"""
import os

ROWS, COLS = 3, 3
MAPPING = "123456789"

X0, Y0 = 150, 170          # первое пересечение
DX, DY = 120, 100          # шаг сетки
W, H = 900, 640

ROW_END_X = X0 + (COLS - 1) * DX + 150   # где строки входят в модуль
COL_END_Y = Y0 + (ROWS - 1) * DY + 130   # где столбцы входят в модуль

FONT = "font-family='Segoe UI, Arial, sans-serif'"
LINE = "stroke='#2b2f36' stroke-width='2' fill='none'"
ROW_COLORS = ["#d64545", "#e08a2e", "#c9a800"]
COL_COLORS = ["#2f6fd6", "#2e9e4f", "#8a4fd6"]

out = []
def add(s): out.append(s)

add(f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}' {FONT}>")
add(f"<rect width='{W}' height='{H}' fill='#ffffff'/>")

# --- заголовки
add(f"<text x='{X0 - 110}' y='40' font-size='15' font-weight='600' fill='#2b2f36'>Матрица кнопок {ROWS}×{COLS}</text>")
add(f"<text x='{X0 - 110}' y='60' font-size='12' fill='#6b7280'>кнопка клетки замыкает свою строку на свой столбец</text>")

# --- модуль строк (справа)
mx, my = ROW_END_X + 10, Y0 - 75
mh = (ROWS - 1) * DY + 120
add(f"<rect x='{mx}' y='{my}' width='170' height='{mh}' rx='8' fill='#f3f4f6' stroke='#9aa0a6' stroke-width='1.5'/>")
add(f"<text x='{mx + 85}' y='{my + 22}' font-size='14' font-weight='700' text-anchor='middle' fill='#2b2f36'>3n_mosfet</text>")
add(f"<text x='{mx + 85}' y='{my + 40}' font-size='11' text-anchor='middle' fill='#6b7280'>слот 0 · outSlots · строки</text>")

# --- модуль столбцов (снизу)
cx, cy = X0 - 45, COL_END_Y + 10
cw = (COLS - 1) * DX + 90
add(f"<rect x='{cx}' y='{cy}' width='{cw}' height='92' rx='8' fill='#f3f4f6' stroke='#9aa0a6' stroke-width='1.5'/>")
add(f"<text x='{cx + cw / 2}' y='{cy + 62}' font-size='14' font-weight='700' text-anchor='middle' fill='#2b2f36'>in_3ch</text>")
add(f"<text x='{cx + cw / 2}' y='{cy + 80}' font-size='11' text-anchor='middle' fill='#6b7280'>слот 1 · inSlots · столбцы</text>")

# --- провода строк
for r in range(ROWS):
    y = Y0 + r * DY
    add(f"<line x1='{X0 - 60}' y1='{y}' x2='{ROW_END_X + 10}' y2='{y}' stroke='{ROW_COLORS[r]}' stroke-width='2.5'/>")
    # пин модуля
    add(f"<circle cx='{ROW_END_X + 10}' cy='{y}' r='4' fill='#ffffff' stroke='{ROW_COLORS[r]}' stroke-width='2'/>")
    add(f"<text x='{ROW_END_X + 22}' y='{y + 4}' font-size='12' fill='#2b2f36'>ch_{r}</text>")
    add(f"<text x='{X0 - 66}' y='{y + 4}' font-size='11' text-anchor='end' fill='#6b7280'>row{r}</text>")

# --- провода столбцов
for c in range(COLS):
    x = X0 + c * DX
    add(f"<line x1='{x}' y1='{Y0 - 60}' x2='{x}' y2='{COL_END_Y + 10}' stroke='{COL_COLORS[c]}' stroke-width='2.5'/>")
    add(f"<circle cx='{x}' cy='{COL_END_Y + 10}' r='4' fill='#ffffff' stroke='{COL_COLORS[c]}' stroke-width='2'/>")
    add(f"<text x='{x}' y='{COL_END_Y + 32}' font-size='12' text-anchor='middle' fill='#2b2f36'>ch_{c}</text>")
    add(f"<text x='{x}' y='{Y0 - 66}' font-size='11' text-anchor='middle' fill='#6b7280'>col{c}</text>")

# --- перекрестья без соединения: маленькая «дужка» на строке над столбцом
for r in range(ROWS):
    y = Y0 + r * DY
    for c in range(COLS):
        x = X0 + c * DX
        add(f"<rect x='{x - 6}' y='{y - 6}' width='12' height='12' fill='#ffffff'/>")
        add(f"<path d='M{x - 6},{y} a6,6 0 0 1 12,0' stroke='{ROW_COLORS[r]}' stroke-width='2.5' fill='none'/>")

# --- кнопки: нормально разомкнутый контакт между строкой и столбцом
for r in range(ROWS):
    y = Y0 + r * DY
    for c in range(COLS):
        x = X0 + c * DX
        ax, ay = x - 40, y            # отвод от строки
        bx, by = x, y + 40            # отвод от столбца
        # выводы контакта
        add(f"<line x1='{ax}' y1='{ay}' x2='{ax}' y2='{ay + 18}' {LINE}/>")
        add(f"<line x1='{bx}' y1='{by}' x2='{bx - 18}' y2='{by}' {LINE}/>")
        add(f"<circle cx='{ax}' cy='{ay + 18}' r='3' fill='#ffffff' stroke='#2b2f36' stroke-width='2'/>")
        add(f"<circle cx='{bx - 18}' cy='{by}' r='3' fill='#ffffff' stroke='#2b2f36' stroke-width='2'/>")
        # подвижный контакт (разомкнут): пластина от клеммы строки в сторону клеммы столбца
        add(f"<line x1='{ax + 2}' y1='{ay + 21}' x2='{bx - 14}' y2='{by - 14}' {LINE}/>")
        # точки присоединения к шинам
        add(f"<circle cx='{ax}' cy='{ay}' r='3' fill='{ROW_COLORS[r]}'/>")
        add(f"<circle cx='{bx}' cy='{by}' r='3' fill='{COL_COLORS[c]}'/>")
        # символ клетки
        sym = MAPPING[r * COLS + c]
        add(f"<rect x='{x + 10}' y='{y + 8}' width='22' height='22' rx='4' fill='#fff7d6' stroke='#c9a800'/>")
        add(f"<text x='{x + 21}' y='{y + 24}' font-size='13' font-weight='600' text-anchor='middle' fill='#2b2f36'>{sym}</text>")

# --- легенда
ly = H - 14
add(f"<text x='{X0 - 110}' y='{ly}' font-size='12' fill='#6b7280'>"
    f"символ клетки = mapping[3·row + col] · строки: 3n_mosfet ch_0…ch_2 · столбцы: in_3ch ch_0…ch_2</text>")

add("</svg>")

dst = os.path.join(os.path.dirname(__file__), '..', 'content', 'Программные модули', '_assets', 'buttonMatrix.svg')
with open(dst, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('OK', dst)
