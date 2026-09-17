"""Схематичные GIF-анимации подсветки для модулей button_*: 24 «пикселя».

    python tools/led_gifs.py            # -> content/Программные модули/_assets/button_*.gif

Линейка: button_smartLed, button_ledBar, button_runFire. Кольцо: button_ledRing,
button_swiperLed. Логика повторяет прошивку (components/buttonLeds) упрощённо.
"""
import colorsys
import math
import os

from PIL import Image, ImageDraw, ImageFont

N = 24
BG = (30, 33, 38)
OFF = (58, 62, 70)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
DT = 40  # мс на кадр

OUT = os.path.join(os.path.dirname(__file__), '..', 'content', 'Программные модули', '_assets')
FONT = None
for cand in ('C:/Windows/Fonts/segoeui.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
    if os.path.exists(cand):
        FONT = ImageFont.truetype(cand, 16)
        break
FONT = FONT or ImageFont.load_default()


def hsv(h, s=1.0, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


def scale(rgb, k):
    k = max(0.0, min(1.0, k))
    return tuple(int(OFF[i] + (rgb[i] - OFF[i]) * k) for i in range(3))


# ---------------------------------------------------------------- раскладки
def row_frame(pixels, label=''):
    cell, gap, pad = 22, 6, 16
    w = pad * 2 + N * cell + (N - 1) * gap
    h = pad * 2 + cell + (26 if label is not None else 0)
    im = Image.new('RGB', (w, h), BG)
    d = ImageDraw.Draw(im)
    for i, c in enumerate(pixels):
        x = pad + i * (cell + gap)
        d.rounded_rectangle([x, pad, x + cell, pad + cell], radius=4, fill=c)
    if label:
        d.text((pad, pad + cell + 6), label, font=FONT, fill=(190, 195, 205))
    return im


def ring_frame(pixels, label=''):
    size, cell, r = 300, 20, 120
    im = Image.new('RGB', (size, size), BG)
    d = ImageDraw.Draw(im)
    for i, c in enumerate(pixels):
        a = -math.pi / 2 + 2 * math.pi * i / N  # пиксель 0 сверху, по часовой
        cx, cy = size / 2 + r * math.cos(a), size / 2 + r * math.sin(a)
        d.rounded_rectangle([cx - cell / 2, cy - cell / 2, cx + cell / 2, cy + cell / 2], radius=4, fill=c)
    if label:
        d.multiline_text((size / 2, size / 2), label, font=FONT, fill=(190, 195, 205), anchor='mm', align='center')
    return im


def save(name, frames):
    path = os.path.join(OUT, name)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=DT, loop=0, optimize=False)
    print('OK', path, len(frames), 'frames')


def hold(frames, frame, n):
    frames.extend([frame] * n)


# ---------------------------------------------------------------- smartLed
def gif_smartLed():
    fr = []
    # default: плавное включение (fadeTime), пауза
    for k in range(20):
        fr.append(row_frame([scale(BLUE, k / 19)] * N, 'default — включение с fadeTime'))
    hold(fr, fr[-1], 15)
    # flash: пульсация min <-> max
    for t in range(60):
        v = 0.5 + 0.5 * math.sin(t / 60 * 4 * math.pi - math.pi / 2)
        fr.append(row_frame([scale(BLUE, v)] * N, 'flash — между minBright и maxBright'))
    # rainbow: вся лента одним цветом, оттенок бежит
    for t in range(60):
        fr.append(row_frame([hsv(t / 60)] * N, 'rainbow — оттенок по кругу'))
    # выключение
    for k in range(20):
        fr.append(row_frame([scale(hsv(0.0), 1 - k / 19)] * N, 'toggleLedState — плавное выключение'))
    hold(fr, fr[-1], 10)
    save('button_smartLed.gif', fr)


# ---------------------------------------------------------------- ledBar
def gif_ledBar():
    fr = []
    seq = list(range(0, N + 1)) + [N] * 10 + list(range(N, -1, -1)) + [0] * 10
    for pos in seq:
        px = [GREEN if i < pos else OFF for i in range(N)]
        fr.append(row_frame(px, 'setPos %2d — заполнение от начала до позиции' % pos))
        fr.append(fr[-1])
    save('button_ledBar.gif', fr)


# ---------------------------------------------------------------- runFire
def gif_runFire():
    fr = []
    L = 12  # effectLen
    for t in range(48):  # rainbow: градиент бежит по ленте
        fr.append(row_frame([hsv((i - t) / N) for i in range(N)], 'animMode rainbow — радуга бежит по ленте'))
    for t in range(48):  # sin: волна яркости
        px = [scale(BLUE, 0.5 + 0.5 * math.sin(2 * math.pi * (i - t) / L)) for i in range(N)]
        fr.append(row_frame(px, 'animMode sin — волна яркости, effectLen = %d' % L))
    for t in range(48):  # sinAbs
        px = [scale(BLUE, abs(math.sin(math.pi * (i - t) / L))) for i in range(N)]
        fr.append(row_frame(px, 'animMode sinAbs — волна без «тёмной» половины'))
    save('button_runFire.gif', fr)


# ---------------------------------------------------------------- ledRing
def spot(pos, length, color):
    px = [OFF] * N
    for k in range(length):
        px[(pos - k) % N] = scale(color, 1 - k / length)
    return px


def gif_ledRing():
    fr = []
    RED = (255, 0, 0)
    for pos in (0, 6, 12, 18):  # default: пятно ставится командой setPos
        f = ring_frame(spot(pos, 1, RED), 'default\nsetPos %d' % pos)
        hold(fr, f, 18)
    for t in range(2 * N):  # run: пятно с хвостом effectLen бежит по кольцу
        fr.append(ring_frame(spot(t % N, 6, RED), 'run\neffectLen 6'))
        fr.append(fr[-1])
    save('button_ledRing.gif', fr)


# ---------------------------------------------------------------- swiperLed
def gif_swiperLed():
    """Фронт яркости идёт через кольцо по оси свайпа, симметрично с обеих сторон."""
    fr = []
    FRONT = 0.35  # ширина фронта в долях диаметра
    for name, ax, sign in (('up', 'y', -1), ('down', 'y', 1), ('left', 'x', -1), ('right', 'x', 1)):
        for t in range(36):
            p = -1.2 + 2.4 * t / 35  # положение фронта по оси, -1..1
            px = []
            for i in range(N):
                a = -math.pi / 2 + 2 * math.pi * i / N
                x, y = math.cos(a), math.sin(a)
                c = (y if ax == 'y' else x) * sign  # координата пикселя вдоль оси свайпа
                d = abs(c - p) / FRONT
                px.append(scale(GREEN, math.cos(d * math.pi / 2) if d < 1 else 0))
            fr.append(ring_frame(px, 'swipe\n' + name))
        hold(fr, ring_frame([OFF] * N, 'swipe\n' + name), 8)
    save('button_swiperLed.gif', fr)


if __name__ == '__main__':
    gif_smartLed()
    gif_ledBar()
    gif_runFire()
    gif_ledRing()
    gif_swiperLed()
