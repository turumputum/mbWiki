# -*- coding: utf-8 -*-
"""Датчики, аналог, дискретные входы-выходы, силовые модули."""
from pages_data import SPECS, HW, SW

# ------------------------------------------------------ аналог и датчики ----

SPECS.append(dict(
    path=SW + 'analog_sw.md',
    manifest='adc1',
    mode='analog',
    trigger='analog_<slot>',
    action=None,
    title='analog',
    tags=['sw', 'input', 'analog'],
    intro='Программный модуль аналогового входа: измеряет напряжение встроенным АЦП и рапортует значение.',
    compat=[(HW + 'in_2ch_hw', 'Модуль два цифровых входа'),
            (HW + 'tenzoButton_hw', 'Модуль тензо-кнопки')],
    compat_note='Модуль работает с любым аппаратным модулем, выводящим аналоговый сигнал на пин слота.',
    principle='''Рапортует об изменении аналогового сигнала на входе, а при заданной опции
**periodic** — ещё и периодически. Разрядность встроенного АЦП 12 бит, то есть
сырое значение лежит в диапазоне 0–4095.

Рабочий диапазон ограничивается опциями **minVal** и **maxVal**, входной делитель
выбирается опцией **dividerMode** под ожидаемое напряжение. Предусмотрен фильтр
«скользящее среднее» (**filterK**) и зона нечувствительности (**deadBand**).

При заданном пороге (**threshold**) модуль работает как дискретный датчик:
рапортует `1` при превышении порога и `0` при возврате. Гистерезис и задержки
подтверждения подавляют дребезг у самого порога.''',
    topic_example='analog_0/event/rawVal',
    report_example='Пример: топик `moduleBox/analog_0/event/rawVal`, payload `2048`.\n\n'
                   'Событие `ratio` рапортуется при поднятом флаге **floatOutput**, '
                   '`threshold` — при заданной опции **threshold**.',
    examples='''```ini
[SLOT_0]
mode = analog
options = dividerMode:5V, filterK:0.1, deadBand:20
;значение аналогового входа уходит в масштабатор
crosslink = analog_0/event/rawVal:@->scaler_6/action/pushVal:@
```
Сырое значение сглаживается фильтром и передаётся в
[[Программные модули/Виртуальные модули/scaler_sw|scaler]] для приведения к нужному диапазону.

```ini
[SLOT_1]
mode = analog
options = threshold:2000, thresholdHysteresis:100, thresholdRiseLag:50
;при превышении порога проиграть трек 0
crosslink = analog_1/event/threshold:1->player_0/action/play:0
```
Дискретный режим: переход в `1` подтверждается 50 мс, гистерезис 100 единиц
не даёт состоянию дребезжать у порога.''',
))

SPECS.append(dict(
    path=SW + 'tenzoButton_sw.md',
    manifest='tenzoButton',
    title='tenzoButton',
    tags=['sw', 'input', 'button', 'analog'],
    intro='Программный модуль тензо-кнопки: нажатие определяется по силе давления на тензодатчик.',
    compat=[(HW + 'tenzoButton_hw', 'Модуль тензо-кнопки')],
    principle='''Рапортует при физическом воздействии на датчик и передаёт силу нажатия.
Порог срабатывания задаётся опцией **threshold**, скорость реакции — опцией
**inertia**: чем больше значение, тем медленнее модуль реагирует на изменение силы.

При поднятом флаге **boolean** модуль работает как дискретная кнопка и рапортует
`1` при нажатии и `0` при отпускании вместо величины силы.''',
    topic_example='tenzoButton_0/event/val',
    report_example='Пример: топик `moduleBox/tenzoButton_0/event/val`, payload `540`.',
    sections=[('Индикация', 'Светодиодный индикатор на плате горит, пока кнопка нажата.')],
    examples='''```ini
[SLOT_3]
mode = tenzoButton
options = boolean, threshold:150
;при нажатии кнопки проиграть трек с индексом два
crosslink = tenzoButton_3/event/val:1->player_0/action/play:2
```
Модуль настроен как дискретная кнопка с порогом срабатывания 150.

```ini
[SLOT_4]
mode = tenzoButton
options = threshold:50, inertia:100, oversample:16
;сила нажатия уходит в масштабатор, тот - в яркость подсветки
crosslink = tenzoButton_4/event/val:@->scaler_6/action/pushVal:@
```''',
))

DIST_PRINCIPLE = '''Датчик опрашивается непрерывно; модуль рапортует расстояние, когда оно изменилось
больше, чем на **deadBand**.

Режим работы задаётся опцией **threshold**:
- `0` — аналоговый режим: рапортуется само расстояние (`distance`) и его доля от
  диапазона измерений (`ratio`);
- больше нуля — дискретный режим: рапортуется `threshold` со значением `1`, когда
  объект ближе порога, и `0`, когда дальше.

Диапазон измерений ограничивается опциями **minVal** и **maxVal**, дребезг у порога
подавляется опциями **debounceGap** и **cooldownTime**, шум — фильтром **filterK**.'''

DIST_REPORT_NOTE = ('Пример: топик `moduleBox/distanceSens_0/event/distance`, payload `156`.\n\n'
                    'В аналоговом режиме (**threshold** = 0) рапортуются `distance` и `ratio`, '
                    'в дискретном — `threshold`.')

DIST_EXAMPLES = '''```ini
[SLOT_3]
mode = %s
options = threshold:%s, filterK:0.05
;при срабатывании датчика проиграть трек с индексом ноль
crosslink = distanceSens_3/event/threshold:1->player_0/action/play:0
```
Датчик настроен как дискретный выход с порогом срабатывания %s и высокой
степенью сглаживания сигнала.

```ini
[SLOT_4]
mode = %s
options = minVal:%s, maxVal:%s, deadBand:20
;расстояние уходит в масштабатор, тот - в яркость подсветки
crosslink = distanceSens_4/event/distance:@->scaler_6/action/pushVal:@
```
Аналоговый режим: рапортуется расстояние в рабочем диапазоне, изменения меньше
20 единиц игнорируются.'''

for mid, tags, intro, indication, thr, lo, hi in [
    ('hlk2410', ['sw', 'input', 'distance', 'uart'],
     'Программный модуль радарного датчика присутствия HLK-LD2410. Рапортует расстояние до объекта в сантиметрах, дальность до 800 см.',
     'Светодиодный индикатор на плате меняет яркость пропорционально расстоянию до объекта.',
     '140', '20', '400'),
    ('benewakeTOF', ['sw', 'input', 'distance', 'uart'],
     'Программный модуль лазерного дальномера Benewake TOF. Рапортует расстояние до объекта в миллиметрах, дальность до 12 м.',
     None, '1500', '200', '6000'),
    ('TOFxxxF', ['sw', 'input', 'distance', 'uart'],
     'Программный модуль лазерных дальномеров серии TOFxxxF: TOF050F — до 500 мм, TOF200F — до 2000 мм, TOF400F — до 4000 мм. Расстояние в миллиметрах.',
     None, '300', '50', '2000'),
    ('sr04m', ['sw', 'input', 'distance', 'uart'],
     'Программный модуль ультразвукового дальномера SR04M в UART-режиме. Рапортует расстояние до объекта в миллиметрах, дальность до 4500 мм.',
     None, '1000', '100', '3000'),
]:
    spec = dict(
        path=SW + mid + '_sw.md',
        manifest=mid,
        title=mid,
        tags=tags,
        intro=intro,
        compat=[(HW + 'uart_hw', 'Модуль интерфейса UART')],
        principle=DIST_PRINCIPLE,
        topic_example='distanceSens_0/event/distance',
        report_example=DIST_REPORT_NOTE,
        examples=DIST_EXAMPLES % (mid, thr, thr, mid, lo, hi),
    )
    if indication:
        spec['sections'] = [('Индикация', indication)]
    SPECS.append(spec)

SPECS.append(dict(
    path=SW + 'rplidarS1_sw.md',
    manifest='rplidarS1',
    title='rplidarS1',
    tags=['sw', 'input', 'distance', 'uart'],
    intro='Программный модуль лидара RPLIDAR S1: измеряет расстояние до ближайшего объекта в заданном секторе углов, дальность до 40 м.',
    compat=[(HW + 'uart_hw', 'Модуль интерфейса UART')],
    principle='''Лидар непрерывно сканирует окружность на 360°. Модуль отбирает точки, попадающие
в сектор между **angleMinVal** и **angleMaxVal** и в диапазон дистанций между
**distMinVal** и **distMaxVal**, после чего рапортует ближайшую из них: расстояние
(`distance`) и её угол (`angle`).

Нулевой угол сдвигается опцией **angleOffset** — так сектор совмещается с реальной
установкой лидара. Флаг **distanceReport** отключает рапорт угла.

При заданном **distThreshold** модуль дополнительно работает как дискретный датчик:
рапортует `threshold` со значением `1`, когда ближайший объект ближе порога.
Гистерезис **thresholdHysteresis** подавляет дребезг у порога.

Ошибки связи с лидаром рапортуются событием `error` текстовой строкой.''',
    topic_example='lidar_0/event/distance',
    report_example='Пример: топик `moduleBox/lidar_0/event/distance`, payload `1250`.',
    examples='''```ini
[SLOT_2]
mode = rplidarS1
options = angleMinVal:150, angleMaxVal:210, distThreshold:1500, thresholdHysteresis:100
;объект ближе полутора метров в секторе перед устройством включает подсветку
crosslink = lidar_2/event/threshold:@->led_0/action/enable:@
```
Сектор шириной 60° перед устройством, порог срабатывания 1500 мм.

```ini
[SLOT_3]
mode = rplidarS1
options = distMaxVal:6000, distanceReport, deadBand:50, filterK:0.2
;дистанция до ближайшего объекта уходит в масштабатор
crosslink = lidar_3/event/distance:@->scaler_6/action/pushVal:@
```''',
))

SPECS.append(dict(
    path=SW + 'swiper_sw.md',
    manifest='swiper',
    title='swiper',
    tags=['sw', 'input', 'i2c'],
    intro='Программный модуль жестового датчика APDS9960: распознаёт свайпы рукой в четырёх направлениях.',
    compat=[(HW + 'i2c_hw', 'Модуль интерфейса I2C')],
    principle='''Датчик подключается по I2C и распознаёт направление движения руки над собой.
Модуль рапортует событие `swipe` строкой `up`, `down`, `left` или `right`.

Флаг **upDownDisable** отключает вертикальные жесты — полезно, когда датчик
установлен так, что различает только горизонтальное движение.''',
    topic_example='swiper_0/event/swipe',
    report_example='Пример: топик `moduleBox/swiper_0/event/swipe`, payload `left`.',
    examples='''```ini
[SLOT_2]
mode = swiper
;свайп влево - предыдущий трек, вправо - следующий
crosslink = swiper_2/event/swipe:left->player_0/action/play:-1, swiper_2/event/swipe:right->player_0/action/play:+1
```

```ini
[SLOT_3]
mode = swiper
options = upDownDisable

[SLOT_4]
mode = button_swiperLed
;жест отыгрывается световым эффектом на подсветке
crosslink = swiper_3/event/swipe:@->led_4/action/swipe:@
```''',
))

SPECS.append(dict(
    path=SW + 'tachometer_sw.md',
    manifest='tachometer',
    title='tachometer',
    tags=['sw', 'input'],
    intro='Программный модуль тахометра: измеряет частоту импульсов на входе — в герцах либо в оборотах в минуту.',
    compat=[(HW + 'in_2ch_hw', 'Модуль два цифровых входа'),
            (HW + 'in_out_hw', 'Модуль вход-выход')],
    principle='''Импульсы считаются аппаратным счётчиком PCNT в окне длиной 1/**refreshRate**;
по окончании окна модуль пересчитывает частоту и рапортует её при изменении.

Опция **divider** задаёт число импульсов на один оборот, **timeQuant** выбирает
единицы: `sec` — герцы, `min` — обороты в минуту. Дребезг подавляется аппаратным
фильтром (**debounceGap**), дрожание показаний — опциями **deadBand** и **filterK**.

При заданном **threshold** модуль дополнительно рапортует дискретное состояние:
`1`, когда частота выше порога, и `0`, когда ниже.

> [!note]
> Периферии PCNT в ESP32-S3 всего четыре, и она делится между модулями
> `tachometer`, [[Программные модули/encoderInc_sw|encoderInc]] и
> [[Программные модули/stepper_sw|stepper]].''',
    topic_example='tachometer_0/event/val',
    report_example='Пример: топик `moduleBox/tachometer_0/event/val`, payload `1450`.',
    examples='''```ini
[SLOT_1]
mode = tachometer
options = divider:2, timeQuant:min, front:rise, deadBand:10
;обороты вентилятора уходят на индикацию
crosslink = tachometer_1/event/val:@->scaler_6/action/pushVal:@
```
Датчик даёт два импульса на оборот, показания в оборотах в минуту, изменения
меньше 10 об/мин не рапортуются.

```ini
[SLOT_2]
mode = tachometer
options = threshold:100, timeQuant:sec
;падение частоты ниже 100 Гц выключает реле
crosslink = tachometer_2/event/threshold:0->relay_3/action/setVal:0
```''',
))

# ------------------------------------------------------------- энкодеры ----

SPECS.append(dict(
    path=SW + 'encoderAS5600_sw.md',
    manifest='encoderAS5600',
    title='encoderAS5600',
    tags=['sw', 'input', 'i2c'],
    intro='Программный модуль абсолютного магнитного энкодера AS5600 по I2C: 12 бит, 4096 позиций на окружность.',
    compat=[(HW + 'i2c_hw', 'Модуль интерфейса I2C')],
    principle='''Рапортует об изменении положения ротора. Окружность делится на **numOfPos**
сегментов — именно в этих единицах отдаётся значение.

Режим задаётся флагом **absolute**:
- без флага — инкрементальный режим: рапортуется приращение с прошлого отсчёта;
- с флагом — абсолютный: рапортуется текущая позиция.

Флаг **floatOutput** переводит вывод в дробное число от 0.0 до 1.0. Нуль сдвигается
опцией **zeroShift**, направление счёта разворачивается флагом **dirInverse**,
дрожание подавляется опциями **deadZone** и **filterK**.''',
    topic_example='encoder_0/event/val',
    report_example='Пример: топик `moduleBox/encoder_0/event/val`, payload `17`.',
    report_payload={'event/val': 'целое либо `0.0`–`1.0`'},
    examples='''```ini
[SLOT_1]
mode = encoderAS5600
options = absolute, floatOutput, numOfPos:24
;положение ротора задаёт громкость проигрывателя
crosslink = encoder_1/event/val:@->scaler_6/action/pushVal:@
```
Абсолютный режим: текущая позиция рапортуется дробным числом от 0.0 до 1.0.

```ini
[SLOT_2]
mode = encoderAS5600
options = numOfPos:36, deadZone:8, filterK:0.3
;вращение по часовой перелистывает треки вперёд
crosslink = encoder_2/event/val:@>0->player_0/action/play:+1
```''',
))

SPECS.append(dict(
    path=SW + 'encoderInc_sw.md',
    manifest='encoderInc',
    title='encoderInc',
    tags=['sw', 'input'],
    intro='Программный модуль инкрементального (обычно оптического) энкодера с квадратурным выходом.',
    compat=[(HW + 'in_2ch_hw', 'Модуль два цифровых входа'),
            (HW + 'in_3ch_hw', 'Модуль три цифровых входа')],
    principle='''Импульсы каналов A и B считаются аппаратным счётчиком PCNT, направление вращения
определяется по их фазе. Опция **divider** задаёт число импульсов на один шаг
позиции, **glitchFilter** отсекает короткие помехи на входе.

Режим задаётся флагом **absolute**:
- без флага — инкрементальный: рапортуется приращение с прошлого отсчёта;
- с флагом — абсолютный: рапортуется позиция в пределах **minVal**–**maxVal**.

Флаг **linearCounter** останавливает счёт на границах диапазона; без него счётчик
зацикливается. Команда `reset` обнуляет позицию.

> [!note]
> Периферии PCNT в ESP32-S3 всего четыре, и она делится между модулями
> `encoderInc`, [[Программные модули/tachometer_sw|tachometer]] и
> [[Программные модули/stepper_sw|stepper]]. Поэтому модуль доступен только
> в слотах 0–3.''',
    topic_example='encoder_0/event/val',
    report_example='Пример: топик `moduleBox/encoder_0/event/val`, payload `-3`.',
    examples='''```ini
[SLOT_0]
mode = encoderInc
options = absolute, linearCounter, minVal:0, maxVal:100, divider:4
;позиция энкодера задаёт целевую позицию шагового двигателя
crosslink = encoder_0/event/val:@->stepper_1/action/moveToAbs:@
```
Абсолютный режим с линейным счётчиком: позиция не выходит за 0–100, четыре
импульса энкодера дают один шаг позиции.

```ini
[SLOT_1]
mode = encoderInc
options = dirInverse, glitchFilter:1500
;каждый щелчок энкодера листает трек
crosslink = encoder_1/event/val:@->player_0/action/shift:@
```''',
))

# ----------------------------------------------- дискретные входы-выходы ----

IN_PRINCIPLE = '''Каналы опрашиваются с периодом **refreshPeriod**, дребезг контактов подавляется
опцией **inDebounceGap**. Каждый канал можно инвертировать флагом `inverse_N`.

Режим рапорта задаётся опцией **logic**:
- `independent` — каналы независимы, каждый рапортует своё состояние (`ch_0`, `ch_1`…);
- `or` — рапортуется `val` со значением `1`, если активен хотя бы один канал;
- `and` — рапортуется `val` со значением `1`, если активны все каналы.'''

SPECS.append(dict(
    path=SW + 'in_2ch_sw.md',
    manifest='in_2ch',
    title='in_2ch',
    tags=['sw', 'input'],
    intro='Программный модуль двух цифровых входов с поддержкой логических операций над каналами.',
    compat=[(HW + 'in_2ch_hw', 'Модуль два цифровых входа')],
    principle=IN_PRINCIPLE,
    topic_example='in_0/event/ch_0',
    report_example='Пример: топик `moduleBox/in_0/event/ch_1`, payload `1`.\n\n'
                   'В режиме `independent` рапортуются `ch_0` и `ch_1`, в режимах `or` и `and` — `val`.',
    examples='''```ini
[SLOT_0]
mode = in_2ch
options = inDebounceGap:100, logic:independent
;первый вход включает реле, второй - выключает
crosslink = in_0/event/ch_0:1->relay_3/action/setVal:1, in_0/event/ch_1:1->relay_3/action/setVal:0
```

```ini
[SLOT_1]
mode = in_2ch
options = logic:and, inverse_0, inverse_1
;оба датчика сработали одновременно - проиграть трек
crosslink = in_1/event/val:1->player_0/action/play:0
```
Логика `and` с инверсией обоих каналов: событие приходит, когда оба входа
замкнуты на землю.''',
))

SPECS.append(dict(
    path=SW + 'in_3ch_sw.md',
    manifest='in_3ch',
    title='in_3ch',
    tags=['sw', 'input'],
    intro='Программный модуль трёх цифровых входов с поддержкой логических операций над каналами.',
    compat=[(HW + 'in_3ch_hw', 'Модуль три цифровых входа')],
    principle=IN_PRINCIPLE,
    topic_example='in_0/event/ch_0',
    report_example='Пример: топик `moduleBox/in_0/event/ch_2`, payload `1`.\n\n'
                   'В режиме `independent` рапортуются `ch_0`, `ch_1` и `ch_2`, '
                   'в режимах `or` и `and` — `val`.',
    examples='''```ini
[SLOT_0]
mode = in_3ch
options = inDebounceGap:50, logic:independent
;три кнопки запускают три разных трека
crosslink = in_0/event/ch_0:1->player_0/action/play:0, in_0/event/ch_1:1->player_0/action/play:1, in_0/event/ch_2:1->player_0/action/play:2
```

```ini
[SLOT_1]
mode = in_3ch
options = logic:or, refreshPeriod:50
;срабатывание любого из трёх датчиков включает подсветку
crosslink = in_1/event/val:@->led_2/action/enable:@
```''',
))

SPECS.append(dict(
    path=SW + 'in_out_sw.md',
    manifest='in_out',
    title='in_out',
    tags=['sw', 'input', 'output'],
    intro='Программный модуль пары «цифровой вход + цифровой выход» в одном слоте.',
    compat=[(HW + 'in_out_hw', 'Модуль вход-выход')],
    principle='''Рапортует об изменении состояния входа и исполняет команды на выходе.
Вход и выход независимы: вход можно инвертировать флагом **inInverse** и
отфильтровать от дребезга опцией **inDebounceGap**, выход — инвертировать флагом
**outInverse** и задать ему стартовое состояние опцией **outDefaultState**.

Выход умеет не только включаться и выключаться, но и переключаться командой
`toggle` и формировать импульс заданной длительности командой `impulse`.''',
    topic_example='in_0/event/val',
    report_example='Пример: топик `moduleBox/in_0/event/val`, payload `1`.',
    examples='''```ini
[SLOT_0]
mode = in_out
options = inDebounceGap:100, outDefaultState:1
;состояние входа повторяется на выходе
crosslink = in_0/event/val:@->out_0/action/setVal:@
```

```ini
[SLOT_1]
mode = in_out
options = inInverse, outInverse
;срабатывание входа даёт импульс полсекунды на выходе
crosslink = in_1/event/val:1->out_1/action/impulse:500
```''',
))

OUT_PRINCIPLE = '''Модуль исполняет входящие команды и состоянием входа не занимается —
событий, кроме `enable`, у него нет.

Каждый канал инвертируется опцией `inverse_N` и получает стартовое состояние
опцией `defState_N`. Помимо прямой установки значения, канал умеет переключаться
командой `toggle` и формировать импульс заданной длительности командой `impulse`.'''

SPECS.append(dict(
    path=SW + 'out_2ch_sw.md',
    manifest='out_2ch',
    title='out_2ch',
    tags=['sw', 'output'],
    intro='Программный модуль двух цифровых выходов.',
    compat=[(HW + 'out_2ch_hw', 'Модуль два цифровых выхода'),
            (HW + '3n_mosfet_hw', 'Модуль три силовых MOSFET-ключа')],
    principle=OUT_PRINCIPLE,
    topic_example='out_0/action/ch_0',
    command_text={'action/ch_0': 'Установить состояние канала 0',
                  'action/ch_1': 'Установить состояние канала 1',
                  'action/ch_0/toggle': 'Переключить состояние канала 0',
                  'action/ch_1/toggle': 'Переключить состояние канала 1',
                  'action/ch_0/impulse': 'Импульс на канале 0, длительность в $мСек$',
                  'action/ch_1/impulse': 'Импульс на канале 1, длительность в $мСек$'},
    command_payload={'action/ch_0': '`0` / `1`', 'action/ch_1': '`0` / `1`'},
    command_example='Пример: топик `moduleBox/out_0/action/ch_1/impulse`, payload `500`.',
    examples='''```ini
[SLOT_0]
mode = out_2ch
options = defState_0:1, inverse_1
;кнопка переключает первый канал, второй даёт импульс
crosslink = button_1/event/press:1->out_0/action/ch_0/toggle:1, button_1/event/longPress:1->out_0/action/ch_1/impulse:1000
```
Канал 0 включён при старте, канал 1 работает с инверсией сигнала.''',
))

SPECS.append(dict(
    path=SW + 'out_3ch_sw.md',
    manifest='out_3ch',
    title='out_3ch',
    tags=['sw', 'output'],
    intro='Программный модуль трёх цифровых выходов.',
    compat=[(HW + '3n_mosfet_hw', 'Модуль три силовых MOSFET-ключа'),
            (HW + 'out_2ch_hw', 'Модуль два цифровых выхода')],
    principle=OUT_PRINCIPLE,
    topic_example='out_0/action/ch_0',
    command_text={'action/ch_0': 'Установить состояние канала 0',
                  'action/ch_1': 'Установить состояние канала 1',
                  'action/ch_2': 'Установить состояние канала 2',
                  'action/ch_0/toggle': 'Переключить состояние канала 0',
                  'action/ch_1/toggle': 'Переключить состояние канала 1',
                  'action/ch_2/toggle': 'Переключить состояние канала 2',
                  'action/ch_0/impulse': 'Импульс на канале 0, длительность в $мСек$',
                  'action/ch_1/impulse': 'Импульс на канале 1, длительность в $мСек$',
                  'action/ch_2/impulse': 'Импульс на канале 2, длительность в $мСек$'},
    command_payload={'action/ch_0': '`0` / `1`', 'action/ch_1': '`0` / `1`',
                     'action/ch_2': '`0` / `1`'},
    command_example='Пример: топик `moduleBox/out_0/action/ch_2`, payload `1`.',
    examples='''```ini
[SLOT_0]
mode = out_3ch
options = defState_0:0, defState_1:0, defState_2:1
;три кнопки управляют тремя каналами
crosslink = button_1/event/press:@->out_0/action/ch_0:@, button_2/event/press:@->out_0/action/ch_1:@, button_3/event/press:@->out_0/action/ch_2:@
```''',
))

SPECS.append(dict(
    path=SW + 'relay_sw.md',
    manifest='relay',
    title='relay',
    tags=['sw', 'output'],
    intro='Программный модуль управления реле: включение, выключение, переключение и импульс заданной длительности.',
    compat=[(HW + 'relay_hw', 'Модуль реле')],
    principle='''Модуль исполняет входящие команды, управляя одним реле. Выход инвертируется
опцией **inverse**, стартовое состояние задаётся опцией **defState**.

Команда `impulse` включает реле на заданное число миллисекунд и выключает
самостоятельно — удобно для управления замками, пускателями и импульсными реле.''',
    topic_example='relay_0/action/setVal',
    command_example='Пример: топик `moduleBox/relay_0/action/impulse`, payload `500`.',
    examples='''```ini
[SLOT_0]
mode = relay
options = defState:1, inverse
;нажатие кнопки переключает реле
crosslink = button_1/event/press:1->relay_0/action/toggle:1
```
Реле включается при старте устройства с инвертированным выходным сигналом.

```ini
[SLOT_1]
mode = relay
;срабатывание датчика открывает замок на две секунды
crosslink = whitelist_6/event/val:1->relay_1/action/impulse:2000
```''',
))

SPECS.append(dict(
    path=SW + 'pwmLeds_sw.md',
    manifest='pwmLeds',
    title='pwmLeds',
    tags=['sw', 'output', 'led'],
    intro='Программный модуль трёх ШИМ-каналов с частотой 5 кГц — для светодиодных лент, ламп и прочих нагрузок с плавной регулировкой.',
    compat=[(HW + '3n_mosfet_hw', 'Модуль три силовых MOSFET-ключа'),
            (HW + 'out_2ch_hw', 'Модуль два цифровых выхода')],
    principle='''Три канала ШИМ трактуются как компоненты цвета R, G и B. Целевой цвет задаётся
опцией **RGBcolor** или командой `setRGB`, режим анимации — опцией **ledMode**.

Яркость меняется плавно: за время **fadeTime** значение переходит между
**minBright** и **maxBright** кадрами с частотой **refreshRate**.

Каналами можно управлять и по отдельности — командой `ch_N/setBright`. Это удобно,
когда к модулю подключены три независимые одноцветные нагрузки, а не одна
RGB-лента.''',
    topic_example='pwmLeds_0/action/setRGB',
    command_text={'action/ch_0/setBright': 'Яркость канала 0',
                  'action/ch_1/setBright': 'Яркость канала 1',
                  'action/ch_2/setBright': 'Яркость канала 2',
                  'action/setIncrement': 'Приращение яркости за кадр — скорость анимации и переходов'},
    command_example='Пример: топик `moduleBox/pwmLeds_0/action/ch_1/setBright`, payload `128`.',
    sections=[('Режимы анимации', '''
- **default** — постоянное свечение целевым цветом.
- **flash** — мигание между **minBright** и **maxBright**.
- **rainbow** — циклический перебор оттенков по палитре HSV.''')],
    examples='''```ini
[SLOT_0]
mode = pwmLeds
options = ledMode:rainbow, fadeTime:5000, RGBcolor:0 0 255
;кнопка включает и выключает подсветку
crosslink = button_1/event/press:@->pwmLeds_0/action/enable:@
```
При включении подсветка плавно переливается по палитре HSV, время перехода
5 секунд.

```ini
[SLOT_1]
mode = pwmLeds
options = ledMode:default, maxBright:200, fadeTime:300
;три канала как три независимые лампы
crosslink = in_2/event/ch_0:1->pwmLeds_1/action/ch_0/setBright:200, in_2/event/ch_0:0->pwmLeds_1/action/ch_0/setBright:0
```''',
))

SPECS.append(dict(
    path=SW + 'stepper_sw.md',
    manifest='stepper',
    title='stepper',
    tags=['sw', 'output', 'motor'],
    intro='Программный модуль управления шаговым двигателем сигналами step-dir через драйвер.',
    compat=[(HW + 'out_2ch_hw', 'Модуль два цифровых выхода'),
            (HW + 'in_out_hw', 'Модуль вход-выход')],
    compat_note='Сигналы step и dir выводятся на пины слота; концевые датчики и датчик нуля '
                'подключаются к другим слотам и передают состояние командами '
                '`setHomingSensor`, `setUpLimit` и `setDownLimit`.',
    principle='''Модуль формирует импульсы step с трапецеидальным профилем скорости: разгон
и торможение идут с ускорением **accel**, максимальная скорость ограничена
опцией **maxSpeed**.

Если задано направление базирования **homingDir**, модуль ищет датчик нуля —
сразу при старте (флаг **goHomeOnStart**) или по команде `goHome`. Ход
ограничивается программно опциями **minVal** и **maxVal** и аппаратно —
командами `setUpLimit` и `setDownLimit` от концевых датчиков.

Положение, скорость и состояние рапортуются при включённых флагах **posReport**,
**speedReport** и **stateReport**, не чаще **refreshRate** раз в секунду.''',
    topic_example='stepper_0/event/pos',
    option_text={
        'accel': '*число(int)*, ускорение и замедление в $шаг/сек^2$. По умолчанию 100.',
        'maxSpeed': '*число(int)*, максимальная скорость в $шаг/сек$. По умолчанию 100.',
        'homingSpeed': '*число(int)*, скорость базирования в $шаг/сек$. '
                       'По умолчанию на четверть меньше **maxSpeed**.',
        'homingTimeout': '*число(int)*, таймаут базирования в $сек$, `0` отключает. По умолчанию 30.',
        'maxVal': '*число(int)*, максимальное положение в шагах — программное ограничение хода. '
                  'По умолчанию ограничение снято.',
        'minVal': '*число(int)*, минимальное положение в шагах — программное ограничение хода. '
                  'По умолчанию ограничение снято.',
        'homingDir': '*строка(enum)*, направление базирования. Значения: `up`, `down`. '
                     'По умолчанию базирование выключено.',
        'dirInverse': '*флаг*, инверсия направления вращения.',
        'posReport': '*флаг*, включить рапорты положения.',
        'speedReport': '*флаг*, включить рапорты скорости.',
        'stateReport': '*флаг*, включить рапорты состояния.',
        'circularCounter': '*флаг*, режим кругового счётчика: положение зацикливается '
                           'между **minVal** и **maxVal**.',
        'goHomeOnStart': '*флаг*, базировать сразу при старте, иначе ждать команду `goHome`.',
    },
    report_payload={'event/pos': 'целое, $шаг$', 'event/speed': 'целое, $шаг/сек$'},
    report_text={'event/state': 'Состояние мотора: `run`, `stop`, `maxVal`, `minVal`, `upLimit` или `downLimit`',
                 'event/homingState': 'Состояние базирования: `disable`, `waitingCommand`, `homing`, `done` или `homingTimeout`'},
    report_example='Пример: топик `moduleBox/stepper_0/event/pos`, payload `1200`.',
    command_text={'action/setHomingSensor': 'Состояние датчика нуля — передаётся из слота, к которому он подключён',
                  'action/setUpLimit': 'Аппаратный лимит хода вверх: `1` запрещает движение в плюс',
                  'action/setDownLimit': 'Аппаратный лимит хода вниз: `1` запрещает движение в минус'},
    command_payload={'action/moveToAbs': 'целое, $шаг$', 'action/moveToInc': 'целое, $шаг$',
                     'action/runSpeed': 'целое, $шаг/сек$', 'action/setMaxSpeed': 'целое, $шаг/сек$',
                     'action/setAccel': 'целое, $шаг/сек^2$',
                     'action/setHomingSensor': '`0` / `1`',
                     'action/setUpLimit': '`0` / `1`', 'action/setDownLimit': '`0` / `1`'},
    command_example='Пример: топик `moduleBox/stepper_0/action/moveToAbs`, payload `1200`.',
    examples='''```ini
[SLOT_0]
mode = stepper
options = maxSpeed:5000, accel:5000, homingDir:down, goHomeOnStart, posReport, stateReport
;концевой датчик из слота 1 сообщает о достижении нуля
crosslink = in_1/event/ch_0:@->stepper_0/action/setHomingSensor:@

[SLOT_1]
mode = in_2ch
```
Максимальная скорость 5000 шагов в секунду при ускорении 5000 $шаг/сек^2$ —
на разгон уходит секунда. При старте двигатель базируется вниз до датчика нуля.

```ini
[SLOT_2]
mode = stepper
options = maxSpeed:2000, accel:1000, minVal:0, maxVal:8000
;позиция энкодера задаёт целевую позицию двигателя
crosslink = encoder_3/event/val:@->stepper_2/action/moveToAbs:@
```''',
    scheme='Программные модули/_assets/stepper.svg',
))
