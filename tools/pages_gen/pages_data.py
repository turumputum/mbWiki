# -*- coding: utf-8 -*-
"""Проза страниц программных модулей. Механика берётся из манифеста."""

HW = 'Аппаратные модули/'
SW = 'Программные модули/'

BTN_GROUP = ('Доступные опции для кнопки:',
             ['buttonInverse', 'buttonDebounceGap', 'longPressTime',
              'doubleClickTime', 'eventFilter'])

BTN_EVENTS_NOTE = ('Пример: топик `moduleBox/button_0/event/longPress`, payload `1`.\n\n'
                   'События `longPress` и `doubleClick` рапортуются только при ненулевых '
                   'опциях **longPressTime** и **doubleClickTime** соответственно.')

BTN_PRINCIPLE = ('Рапортует об изменении состояния кнопки: нажатие, отпускание, '
                 'а при включённых опциях — длинное и двойное нажатие. '
                 'Подсветкой управляет по командам и внутренним связям.')

SPECS = []

# ---------------------------------------------------------------- кнопки ----

SPECS.append(dict(
    path=SW + 'button_led_sw.md',
    manifest='button_led',
    title='button_led',
    tags=['sw', 'button', 'led'],
    intro='Программный модуль для кнопки с обычным (одноцветным) светодиодом подсветки.',
    compat=[(HW + 'button_led_hw', 'Модуль кнопка с подсветкой'),
            (HW + 'in_out_hw', 'Модуль вход-выход')],
    principle=BTN_PRINCIPLE + '''

Яркость меняется плавно: за время **fadeTime** значение переходит от **minBright**
к **maxBright** и обратно, кадрами с частотой **ledRefreshRate**.''',
    topic_example='button_0/event/press',
    option_groups=[
        BTN_GROUP,
        ('Доступные опции для подсветки:',
         ['ledInverse', 'ledDefaultState', 'minBright', 'maxBright',
          'fadeTime', 'ledMode', 'ledRefreshRate']),
        ('Общие опции:', ['buttonRefreshRate']),
    ],
    option_text={
        'ledRefreshRate': '*число(int)*, частота перерисовки подсветки, кадров в секунду. '
                          'Диапазон 1–4096. По умолчанию 40.',
        'buttonRefreshRate': '*число(int)*, частота опроса кнопки, кадров в секунду. '
                             'Диапазон 1–4096. По умолчанию 40.',
    },
    report_example=BTN_EVENTS_NOTE,
    command_text={'action/enable': 'Включить (`1`) или выключить (`0`) подсветку'},
    command_example='Пример: топик `moduleBox/led_0/action/setMaxBright`, payload `200`.',
    sections=[('Режимы анимации', '''
- **none** — без анимации. В состоянии «включено» яркость равна **maxBright**, в состоянии «выключено» — **minBright**.
- **flash** — вспышки с равными промежутками времени, от **minBright** до **maxBright**.''')],
    examples='''```ini
[SLOT_0]
mode = button_led
options = ledMode:flash, minBright:0, maxBright:255, fadeTime:500
;включить подсветку при нажатии кнопки, погасить при отпускании
crosslink = button_0/event/press:1->led_0/action/enable:1, button_0/event/press:0->led_0/action/enable:0
```
При активации подсветка плавно моргает: каждый кадр текущее значение яркости
изменяется на рассчитанное приращение, после достижения максимума яркость
начинает уменьшаться.

```ini
[SLOT_1]
mode = button_led
options = longPressTime:1000, eventFilter
;короткое нажатие переключает подсветку, длинное - перезагружает устройство
crosslink = button_1/event/press:1->led_1/action/toggleLedState:1, button_1/event/longPress:1->system/action/restart:1
```
Флаг **eventFilter** подавляет короткое событие `press`, когда сработало длинное
нажатие — иначе оба события пришли бы одновременно.''',
))

SPECS.append(dict(
    path=SW + 'button_smartLed_sw.md',
    manifest='button_smartLed',
    title='button_smartLed',
    tags=['sw', 'button', 'smartLed'],
    intro='Программный модуль для кнопки с подсветкой на адресных светодиодах (WS2812 и совместимых).',
    compat=[(HW + 'button_smartLed_hw', 'Модуль кнопка с управляемой подсветкой')],
    principle=BTN_PRINCIPLE + '''

Все светодиоды ленты светятся одним цветом, заданным опцией **RGBcolor** или
командой `setRGB`. Анимация выбирается опцией **ledMode**.''',
    topic_example='button_0/event/press',
    option_groups=[
        BTN_GROUP,
        ('Доступные опции для подсветки:',
         ['numOfLed', 'ledInverse', 'ledEnableOnStart', 'minBright', 'maxBright',
          'RGBcolor', 'ledMode', 'fadeTime', 'periodicUpdate']),
        ('Общие опции:', ['refreshRate']),
    ],
    option_text={'refreshRate': '*число(int)*, частота обновления, кадров в секунду. '
                                'Задаёт период опроса кнопки и период перерисовки ленты. '
                                'Диапазон 1–4096. По умолчанию 40 для кнопки и 30 для подсветки.'},
    report_example=BTN_EVENTS_NOTE,
    command_text={'action/enable': 'Включить (`1`) или выключить (`0`) подсветку'},
    command_example='Пример: топик `moduleBox/led_0/action/setRGB`, payload `255 0 0`.',
    sections=[('Режимы анимации', '''
- **default** — статичное свечение. В состоянии «включено» яркость равна **maxBright**, в состоянии «выключено» — **minBright**.
- **flash** — вспышки с равными промежутками времени, от **minBright** до **maxBright**.
- **rainbow** — переливание цветов по палитре HSV.''')],
    examples='''```ini
[SLOT_0]
mode = button_smartLed
options = ledMode:flash, minBright:0, maxBright:127, RGBcolor:255 0 0, fadeTime:500
;включить подсветку при нажатии кнопки
crosslink = button_0/event/press:1->led_0/action/enable:1
```
При активации подсветка плавно моргает красным цветом в половину яркости.

```ini
[SLOT_1]
mode = button_smartLed
options = numOfLed:12, ledMode:rainbow, maxBright:200
;двойное нажатие переключает режим на статичный
crosslink = button_1/event/doubleClick:1->led_1/action/setMode:default
```''',
))

SPECS.append(dict(
    path=SW + 'button_ledRing_sw.md',
    manifest='button_ledRing',
    title='button_ledRing',
    tags=['sw', 'button', 'smartLed'],
    intro='Программный модуль для кнопки со светодиодным кольцом: световое пятно ставится в заданную позицию либо бежит по кольцу.',
    compat=[(HW + 'button_smartLed_hw', 'Модуль кнопка с управляемой подсветкой')],
    principle=BTN_PRINCIPLE + '''

Подсветка работает как кольцо позиций: **numOfPos** задаёт число дискретных
положений светового пятна, **effectLen** — его длину в светодиодах.
Позиция устанавливается командой `setPos` — так подсвечивается, например,
[[Устройства/spinner|спиннер]].''',
    topic_example='button_0/event/press',
    option_groups=[
        BTN_GROUP,
        ('Доступные опции для подсветки:',
         ['numOfLed', 'numOfPos', 'effectLen', 'offset', 'dirInverse',
          'ledDefaultState', 'minBright', 'maxBright', 'increment',
          'RGBcolor', 'ledMode', 'periodicUpdate']),
        ('Общие опции:', ['refreshRate']),
    ],
    option_text={'refreshRate': '*число(int)*, частота обновления, кадров в секунду. '
                                'Задаёт период опроса кнопки и период перерисовки кольца. '
                                'По умолчанию 40 для кнопки и 30 для подсветки.'},
    report_example=BTN_EVENTS_NOTE,
    command_text={'action/enable': 'Включить (`1`) или выключить (`0`) подсветку'},
    sections=[('Режимы анимации', '''
- **default** — световое пятно стоит статично в позиции, заданной командой `setPos`.
- **run** — пятно движется по кольцу, скорость задаётся опцией **increment**.''')],
    examples='''```ini
[SLOT_2]
mode = button_ledRing
options = RGBcolor:255 0 0, ledMode:run, effectLen:20
;состояние кнопки передаётся в подсветку
crosslink = button_2/event/press:@->led_2/action/enable:@
```
Красное пятно длиной 20 светодиодов бежит по кольцу, пока кнопка нажата.

```ini
[SLOT_3]
mode = button_ledRing
options = numOfLed:24, numOfPos:24, ledMode:default
;позиция энкодера задаёт положение светового пятна
crosslink = encoder_0/event/val:@->led_3/action/setPos:@
```''',
))

SPECS.append(dict(
    path=SW + 'button_ledBar_sw.md',
    manifest='button_ledBar',
    title='button_ledBar',
    tags=['sw', 'button', 'smartLed'],
    intro='Программный модуль для кнопки со шкалой заполнения на адресных светодиодах: лента светится от начала до заданной позиции.',
    compat=[(HW + 'button_smartLed_hw', 'Модуль кнопка с управляемой подсветкой')],
    principle=BTN_PRINCIPLE + '''

Подсветка работает как линейная шкала: команда `setPos` задаёт уровень
заполнения, светодиоды от начала ленты до этой позиции горят цветом **RGBcolor**,
остальные — с яркостью **minBright**. Флаг **dirInverse** разворачивает
направление заполнения.''',
    topic_example='button_0/event/press',
    option_groups=[
        BTN_GROUP,
        ('Доступные опции для шкалы:',
         ['numOfLed', 'numOfPos', 'offset', 'dirInverse', 'ledDefaultState',
          'minBright', 'maxBright', 'increment', 'RGBcolor', 'periodicUpdate']),
        ('Общие опции:', ['refreshRate']),
    ],
    option_text={'refreshRate': '*число(int)*, частота обновления, кадров в секунду. '
                                'Задаёт период опроса кнопки и период перерисовки ленты. '
                                'По умолчанию 40 для кнопки и 30 для подсветки.'},
    report_example=BTN_EVENTS_NOTE,
    command_text={'action/enable': 'Включить (`1`) или выключить (`0`) подсветку'},
    examples='''```ini
[SLOT_0]
mode = button_ledBar
options = numOfLed:30, numOfPos:30, RGBcolor:0 255 0, maxBright:180
;значение аналогового входа отображается уровнем шкалы
crosslink = analog_1/event/rawVal:@->led_0/action/setPos:@
```
Зелёная шкала из 30 светодиодов показывает текущее значение аналогового входа.

```ini
[SLOT_1]
mode = button_ledBar
options = numOfLed:16, dirInverse, RGBcolor:255 128 0
;каждое нажатие увеличивает счётчик, счётчик задаёт уровень шкалы
crosslink = button_1/event/press:1->counter_6/action/set:+1
```''',
))

SPECS.append(dict(
    path=SW + 'button_runFire_sw.md',
    manifest='button_runFire',
    title='button_runFire',
    tags=['sw', 'button', 'smartLed'],
    intro='Программный модуль для кнопки с бегущим световым эффектом на ленте адресных светодиодов.',
    compat=[(HW + 'button_smartLed_hw', 'Модуль кнопка с управляемой подсветкой')],
    principle='''Рапортует об изменении состояния кнопки. В активном состоянии формирует бегущий
световой эффект: каждый цикл обновления сдвигает массив пикселей и рассчитывает
новый пиксель в зависимости от выбранного режима анимации. В неактивном состоянии
плавно гасит ленту до минимальной яркости со скоростью **increment**.''',
    topic_example='button_0/event/press',
    option_groups=[
        BTN_GROUP,
        ('Доступные опции для подсветки:',
         ['numOfLed', 'ledsPerPixel', 'effectLen', 'offset', 'ledInverse',
          'ledDefaultState', 'minBright', 'maxBright', 'increment',
          'RGBcolor', 'animMode', 'periodicUpdate']),
        ('Общие опции:', ['refreshRate']),
    ],
    option_text={'refreshRate': '*число(int)*, частота обновления, кадров в секунду. '
                                'Задаёт период опроса кнопки и период перерисовки ленты. '
                                'По умолчанию 40 для кнопки и 30 для подсветки.',
                 'ledInverse': '*флаг*, инверсия направления эффекта. Без флага движение '
                               'идёт от 0 к **numOfLed**, с флагом — от конца к началу.'},
    report_example=BTN_EVENTS_NOTE,
    command_text={'action/enable': 'Включить (`1`) или выключить (`0`) эффект'},
    sections=[('Режимы анимации', '''
- **rainbow** — бегущая радуга. Каждый новый пиксель получает следующий оттенок цветового круга HSV с максимальной насыщенностью и яркостью **maxBright**.
- **sin** — синусоидальная яркость с периодом **effectLen**. В положительной части синусоиды яркость плавно меняется от **minBright** до **maxBright**, в отрицательной — фиксируется на **minBright**.
- **sinAbs** — то же, но отрицательная часть синусоиды отражается (берётся модуль), создавая непрерывный волнообразный эффект.''')],
    examples='''```ini
[SLOT_0]
mode = button_runFire
options = numOfLed:60, animMode:rainbow, maxBright:200, refreshRate:30
;включить эффект по нажатию, выключить по отпусканию
crosslink = button_0/event/press:1->led_0/action/enable:1, button_0/event/press:0->led_0/action/enable:0
```
Лента из 60 светодиодов с эффектом бегущей радуги, яркость ограничена значением 200.

```ini
[SLOT_1]
mode = button_runFire
options = numOfLed:30, animMode:sin, effectLen:10, RGBcolor:255 0 0, minBright:20, maxBright:255, increment:3
;переключить эффект по нажатию
crosslink = button_1/event/press:1->led_1/action/toggleLedState:1
```
Лента из 30 светодиодов с синусоидальным красным эффектом. Период синусоиды —
10 пикселей, плавный переход с приращением 3.''',
))

SPECS.append(dict(
    path=SW + 'button_swiperLed_sw.md',
    manifest='button_swiperLed',
    title='button_swiperLed',
    tags=['sw', 'button', 'smartLed'],
    intro='Программный модуль для кнопки с подсветкой, поддерживающей световые эффекты свайпа в четырёх направлениях.',
    compat=[(HW + 'button_smartLed_hw', 'Модуль кнопка с управляемой подсветкой')],
    principle=BTN_PRINCIPLE + '''

По команде `swipe` лента отыгрывает анимацию проведения в заданном направлении:
`up`, `down`, `left` или `right`. Эффект удобно связывать с
[[Программные модули/swiper_sw|жестовым датчиком swiper]].''',
    topic_example='button_0/event/press',
    option_groups=[
        BTN_GROUP,
        ('Доступные опции для подсветки:',
         ['numOfLed', 'offset', 'ledDefaultState', 'minBright', 'maxBright', 'RGBcolor']),
        ('Общие опции:', ['refreshRate']),
    ],
    option_text={'refreshRate': '*число(int)*, частота обновления, кадров в секунду. '
                                'Задаёт период опроса кнопки и период перерисовки ленты. '
                                'По умолчанию 40 для кнопки и 25 для подсветки.'},
    report_example=BTN_EVENTS_NOTE,
    command_text={'action/enable': 'Включить (`1`) или выключить (`0`) подсветку'},
    examples='''```ini
[SLOT_2]
mode = button_swiperLed
options = RGBcolor:0 255 0
;нажатие и отпускание кнопки запускают свайпы в разные стороны
crosslink = button_2/event/press:1->led_2/action/swipe:down, button_2/event/press:0->led_2/action/swipe:up
```

```ini
[SLOT_3]
mode = button_swiperLed
options = numOfLed:16, RGBcolor:0 128 255

[SLOT_4]
mode = swiper
;жест руки над датчиком отыгрывается подсветкой
crosslink = swiper_4/event/swipe:@->led_3/action/swipe:@
```

![[Программные модули/_assets/swiperLed.gif]]''',
))

SPECS.append(dict(
    path=SW + 'buttonMatrix_sw.md',
    manifest='buttonMatrix',
    title='buttonMatrix',
    tags=['sw', 'button', 'input'],
    intro='Программный модуль матрицы кнопок: сканирует сетку «выходы × входы» и рапортует символ нажатой клетки.',
    compat=[(HW + 'in_2ch_hw', 'Модуль два цифровых входа'),
            (HW + 'out_2ch_hw', 'Модуль два цифровых выхода')],
    compat_note='Матрица занимает несколько слотов: слоты-выходы перечисляются в опции '
                '**outSlots**, слоты-входы — в **inSlots**. Сам модуль объявляется в одном '
                'слоте и управляет остальными.',
    principle='''Модуль поочерёдно активирует слоты-выходы и опрашивает слоты-входы. Пересечение
активного выхода и сработавшего входа даёт клетку матрицы; её символ берётся из
строки **mapping** и рапортуется событием `key`.

Порядок символов в **mapping** — построчный: сначала все входы первого выхода,
затем второго и так далее. Длина строки должна быть равна произведению числа
выходов на число входов.''',
    topic_example='buttonMatrix_0/event/key',
    report_example='Пример: топик `moduleBox/buttonMatrix_0/event/key`, payload `5`.',
    examples='''```ini
[SLOT_0]
mode = buttonMatrix
options = outSlots:0 1, inSlots:2 3, mapping:1234
;нажатие клетки '1' запускает трек 0
crosslink = buttonMatrix_0/event/key:1->player_0/action/play:0
```
Матрица 2×2: выходы в слотах 0 и 1, входы в слотах 2 и 3. Клетки обозначены
символами `1`, `2`, `3`, `4`.

```ini
[SLOT_0]
mode = buttonMatrix
options = outSlots:0 1 2, inSlots:3 4 5, mapping:123456789
;набранные символы собираются в строку коллектором
crosslink = buttonMatrix_0/event/key:@->collector_6/action/add:@
```
Клавиатура 3×3 с цифрами: символы уходят в
[[Программные модули/Виртуальные модули/collector_sw|collector]], который собирает
из них строку — например код доступа.''',
))
