# -*- coding: utf-8 -*-
"""Виртуальные модули, звук, служебные."""
from pages_data import SPECS, HW, SW

VIRT = SW + 'Виртуальные модули/'
SOUND = SW + 'Звуковые модули/'
CL = '[[Платформа moduleBox/CrossLink|внутренними связями]]'

# ---------------------------------------------------------- виртуальные ----

SPECS.append(dict(
    path=VIRT + 'startup_sw.md',
    manifest='startup',
    title='startup',
    tags=['sw', 'virtual'],
    virtual=True,
    intro='Виртуальный модуль, отправляющий сообщение при запуске устройства.',
    principle='''Рапортует один раз при старте — связанные с этим событием действия выполняются
единожды при включении устройства. Опция **delay** задерживает рапорт, чтобы
дождаться инициализации остальных модулей и сетевых служб.

Применяется для установки начального состояния: включить подсветку, выставить
громкость, запустить фоновый трек.''',
    topic_example='startup_6/event/started',
    report_example='Пример: топик `moduleBox/startup_6/event/started`, payload `1`.',
    examples='''```ini
[SLOT_6]
mode = startup
options = delay:2000
;через две секунды после включения запустить фоновый трек и зажечь подсветку
crosslink = startup_6/event/started:1->player_0/action/play:0, startup_6/event/started:1->led_1/action/enable:1
```''',
))

SPECS.append(dict(
    path=VIRT + 'counter_sw.md',
    manifest='counter',
    title='counter',
    tags=['sw', 'virtual'],
    virtual=True,
    intro='Виртуальный модуль счётчика: хранит целое значение, принимает абсолютные и инкрементальные команды.',
    principle='''Модуль хранит целочисленное значение. Команда `set` принимает как абсолютное
значение, так и приращение с префиксом `+` или `-`. Рапортует при каждом изменении.

При заданном пороге (**threshold**) вместо абсолютного значения рапортуется
дискретное состояние: `0`, пока значение меньше порога, и `1` начиная с него.

Флаг **circularCounter** зацикливает счёт: при переполнении значение сбрасывается
к противоположной границе диапазона **minVal**–**maxVal**.''',
    topic_example='counter_6/event/val',
    option_text={
        'maxVal': '*число(int)*, максимальное значение счётчика. По умолчанию максимум int32.',
        'minVal': '*число(int)*, минимальное значение счётчика. По умолчанию 0.',
        'threshold': '*число(int)*, пороговое значение. При ненулевом пороге модуль рапортует '
                     'дискретное состояние вместо абсолютного значения. По умолчанию 0 — порог выключен.',
        'circularCounter': '*флаг*, при переполнении сбрасывать значение к противоположной границе диапазона.',
    },
    command_text={'action/set': 'Установить значение — абсолютное либо приращение с префиксом `+` / `-`'},
    command_payload={'action/set': 'целое либо `+N` / `-N`'},
    report_example='Пример: топик `moduleBox/counter_6/event/val`, payload `4`.',
    examples='''```ini
[SLOT_6]
mode = counter
options = minVal:0, maxVal:10, circularCounter
;каждое нажатие кнопки увеличивает счётчик
crosslink = button_0/event/press:1->counter_6/action/set:+1
```
Циклический счётчик от 0 до 10: после 10 следующий инкремент даёт 0.

```ini
[SLOT_7]
mode = counter
options = threshold:5, minVal:0, maxVal:100
;одна кнопка увеличивает счётчик, другая уменьшает
crosslink = button_0/event/press:1->counter_7/action/set:+1, button_1/event/press:1->counter_7/action/set:-1
```
Счётчик с порогом 5: пока значение меньше 5 — рапортуется `0`, с 5 и выше — `1`.''',
))

SPECS.append(dict(
    path=VIRT + 'timer_sw.md',
    manifest='timer',
    title='timer',
    tags=['sw', 'virtual'],
    virtual=True,
    intro='Виртуальный модуль таймера: рапортует по истечении заданного времени.',
    principle='''Модуль ждёт команду `start`. Время отсчёта берётся из параметра команды, а если
он не задан или равен нулю — из опции **time**. По истечении времени модуль
рапортует событие `timerEnd`.

Отсчёт можно прервать в любой момент командой `stop`. Повторный `start` до
срабатывания перезапускает отсчёт с начала.''',
    topic_example='timer_6/event/timerEnd',
    command_payload={'action/start': 'целое, $мСек$ (необязательно)'},
    report_example='Пример: топик `moduleBox/timer_6/event/timerEnd`, payload `1`.',
    examples='''```ini
[SLOT_6]
mode = timer
options = time:30000
;нажатие кнопки запускает таймер, по истечении - гаснет подсветка
crosslink = timer_6/event/timerEnd:1->led_0/action/enable:0
```

```ini
[SLOT_7]
mode = timer
;датчик присутствия перезапускает отсчёт, тишина в пять секунд останавливает трек
crosslink = timer_7/event/timerEnd:1->player_0/action/stop:1
```
Запуск таймера с нужным временем приходит извне или
''' + CL + ''': `distanceSens_0/event/threshold:1->timer_7/action/start:5000`.''',
))

SPECS.append(dict(
    path=VIRT + 'random_sw.md',
    manifest='random',
    title='random',
    tags=['sw', 'virtual'],
    virtual=True,
    intro='Виртуальный модуль генератора случайных чисел.',
    principle='''По команде `generate` модуль выдаёт случайное целое число и рапортует его.
Диапазон определяется параметром команды:
- без параметра — диапазон из опций **minVal**–**maxVal**;
- одно число `N` — диапазон от 0 до `N`;
- два числа через пробел — указанный диапазон.''',
    topic_example='random_6/event/val',
    option_text={
        'maxVal': '*число(int)*, верхняя граница диапазона генерации. По умолчанию максимум int32.',
        'minVal': '*число(int)*, нижняя граница диапазона генерации. По умолчанию 0.',
    },
    command_payload={'action/generate': '— либо `N` / `N M`'},
    report_example='Пример: топик `moduleBox/random_6/event/val`, payload `7`.',
    examples='''```ini
[SLOT_6]
mode = random
options = minVal:1, maxVal:10
;нажатие кнопки генерирует число от 1 до 10
crosslink = button_0/event/press:1->random_6/action/generate:1
```

```ini
[SLOT_7]
mode = random
options = minVal:0, maxVal:5
;случайное число используется как индекс трека
crosslink = button_0/event/press:1->random_7/action/generate:1, random_7/event/val:@->player_0/action/play:@
```''',
))

SPECS.append(dict(
    path=VIRT + 'flywheel_sw.md',
    manifest='flywheel',
    title='flywheel',
    tags=['sw', 'virtual'],
    virtual=True,
    intro='Виртуальный модуль «маховик»: счётчик, значение которого само постепенно уменьшается.',
    principle='''Модуль хранит числовое значение, которое каждые **period** миллисекунд
уменьшается на **decrement**. Значение увеличивается или задаётся командой
`setCount` — абсолютно либо приращением с префиксом `+` или `-`.

Абсолютное значение рапортуется событием `count`. При заданном пороге
(**threshold**) модуль дополнительно рапортует `val` — дискретное состояние
`0` или `1`.

Применяется для логики «активность»: пока поступают команды увеличения, значение
держится выше порога; как только активность прекращается, значение сползает
к минимуму и состояние переключается.''',
    topic_example='flywheel_6/event/count',
    command_text={'action/setCount': 'Установить значение счётчика — абсолютное либо приращение с префиксом `+` / `-`'},
    command_payload={'action/setCount': 'целое либо `+N` / `-N`'},
    report_example='Пример: топик `moduleBox/flywheel_6/event/count`, payload `8`.',
    examples='''```ini
[SLOT_6]
mode = flywheel
options = threshold:3, maxVal:10, decrement:0.5, period:200
;каждое нажатие кнопки добавляет единицу
crosslink = button_0/event/press:1->flywheel_6/action/setCount:+1, flywheel_6/event/val:@->led_0/action/enable:@
```
Каждые 200 мс значение уменьшается на 0.5, то есть на 2.5 в секунду. Чтобы
удерживать состояние активным, кнопку нужно нажимать не реже чем раз в секунду.

```ini
[SLOT_7]
mode = flywheel
options = maxVal:100, minVal:0, decrement:1, period:1000
;интенсивность нажатий задаёт яркость подсветки
crosslink = button_0/event/press:1->flywheel_7/action/setCount:+10, flywheel_7/event/count:@->pwmLeds_1/action/setMaxBright:@
```''',
))

SPECS.append(dict(
    path=VIRT + 'scaler_sw.md',
    manifest='scaler',
    title='scaler',
    tags=['sw', 'virtual'],
    virtual=True,
    intro='Виртуальный модуль масштабирования: линейно приводит входное значение из одного диапазона в другой.',
    principle='''Модуль принимает значение командой `pushVal`, линейно пересчитывает его из
диапазона **inputMinVal**–**inputMaxVal** в диапазон
**outputMinVal**–**outputMaxVal** и рапортует событием `result`.

Опция **zeroDeadZone** задаёт мёртвую зону вокруг нуля — входные значения внутри
неё дают на выходе ноль. Это убирает дрожание около центра у джойстиков
и потенциометров.''',
    topic_example='scaler_6/event/result',
    report_example='Пример: топик `moduleBox/scaler_6/event/result`, payload `128`.',
    examples='''```ini
[SLOT_6]
mode = scaler
options = inputMinVal:0, inputMaxVal:4095, outputMinVal:0, outputMaxVal:255
;значение аналогового входа приводится к диапазону яркости
crosslink = scaler_6/event/result:@->pwmLeds_1/action/setMaxBright:@
```
Значение АЦП 0–4095 приводится к 0–255. Источник подаёт значение командой
`scaler_6/action/pushVal`.

```ini
[SLOT_7]
mode = scaler
options = inputMinVal:0, inputMaxVal:255, outputMinVal:0, outputMaxVal:8000, zeroDeadZone:10
;позиция энкодера приводится к позиции шагового двигателя
crosslink = scaler_7/event/result:@->stepper_1/action/moveToAbs:@
```''',
))

SPECS.append(dict(
    path=VIRT + 'collector_sw.md',
    manifest='collector',
    title='collector',
    tags=['sw', 'virtual'],
    virtual=True,
    intro='Виртуальный модуль-накопитель: собирает поступающие символы в строку.',
    principle='''Каждая команда `add` дописывает значение в конец строки. Строка рапортуется
событием `val`, когда её длина достигла **stringMaxLenght** либо когда после
последнего символа прошло **waitingTime** миллисекунд. После рапорта строка
очищается; сбросить её досрочно можно командой `clear`.

Применяется в паре с [[Программные модули/dialer_sw|номеронабирателем]],
[[Программные модули/buttonMatrix_sw|матрицей кнопок]] или считывателем карт —
собранная строка обычно уходит на проверку в
[[Программные модули/Виртуальные модули/whitelist_sw|whitelist]].''',
    topic_example='collector_6/event/val',
    report_example='Пример: топик `moduleBox/collector_6/event/val`, payload `1234567`.',
    examples='''```ini
[SLOT_6]
mode = collector
options = stringMaxLenght:4, waitingTime:5000
;цифры с матрицы кнопок собираются в код, код уходит на проверку
crosslink = collector_6/event/val:@->whitelist_7/action/check:@

[SLOT_0]
mode = buttonMatrix
options = outSlots:0 1, inSlots:2 3, mapping:1234
crosslink = buttonMatrix_0/event/key:@->collector_6/action/add:@
```
Код из четырёх символов собирается и проверяется по списку. Если за пять секунд
код не дописан, накопленное рапортуется как есть.''',
))

SPECS.append(dict(
    path=VIRT + 'whitelist_sw.md',
    manifest='whitelist',
    title='whitelist',
    tags=['sw', 'virtual'],
    virtual=True,
    intro='Виртуальный модуль списка разрешений: сверяет входящую строку со списком в файле на носителе.',
    principle='''Команда `check` сравнивает переданную строку со строками файла **filename**.
При совпадении выполняются связи, объявленные для этой строки в самом файле;
если совпадений нет, модуль рапортует событие `noMatches`.

Файл списка лежит в корне носителя, по одной записи на строку. Сменить файл
на лету можно командой `setFile`. Если файла нет, устройство создаст файл ошибки.

Применяется с [[Программные модули/dialer_sw|номеронабирателем]], считывателем
RFID-карт или [[Программные модули/Виртуальные модули/collector_sw|коллектором]] —
всем, что даёт на входе строку-идентификатор.''',
    topic_example='whitelist_6/event/noMatches',
    command_text={'action/check': 'Проверить строку по списку',
                  'action/setFile': 'Сменить файл списка на лету — имя файла в корне носителя'},
    report_example='Пример: топик `moduleBox/whitelist_6/event/noMatches`, payload `1`.',
    examples='''```ini
[SLOT_6]
mode = whitelist
options = filename:my-list.txt
;если строки нет в списке - проиграть трек с инструкцией
crosslink = whitelist_6/event/noMatches:1->player_0/action/play:1
```''',
))

SPECS.append(dict(
    path=VIRT + 'masquerade_sw.md',
    manifest='masquerade',
    title='masquerade',
    tags=['sw', 'virtual'],
    virtual=True,
    intro='Виртуальный модуль-ретранслятор: перенаправляет входящие значения в другой, «замаскированный» топик.',
    principle='''Значение, поступившее командой `push`, публикуется в топик, заданный опцией
**mask**. Применяется для переименования топиков, маршрутизации сообщений между
устройствами и агрегации событий разных модулей в один поток.

==База топика действия (`masquerade_<slot>`) и база топика события
(`masq_<slot>`) у этого модуля различаются.==''',
    topic_example='masquerade_6/action/push',
    report_example='Пример: топик `moduleBox/masq_6/event/val`, payload `1`.',
    examples='''```ini
[SLOT_6]
mode = masquerade
options = mask:zone_1/trigger
;нажатие кнопки уходит во внешний топик zone_1/trigger
crosslink = button_0/event/press:@->masquerade_6/action/push:@
```

```ini
[SLOT_7]
mode = masquerade
options = mask:player_control/play
;события двух разных датчиков сводятся в один топик
crosslink = distanceSens_1/event/threshold:1->masquerade_7/action/push:1, tenzoButton_2/event/val:1->masquerade_7/action/push:1
```''',
))

SPECS.append(dict(
    path=VIRT + 'conductor_sw.md',
    manifest='conductor',
    title='conductor',
    tags=['sw', 'virtual', 'motor'],
    virtual=True,
    intro='Виртуальный модуль позиционирования: по текущей и целевой позиции выдаёт команды движения приводу.',
    principle='''Модуль принимает текущую позицию от энкодера (`currentPos`) и целевую позицию
(`targetPos`). Он вычисляет направление движения и рапортует `runUp` или
`runDown`; по достижении цели либо по истечении **timeout** рапортует `stop`.

Флаг **multiTurn** включает многооборотную кинематику: модуль выбирает кратчайший
путь к цели через точку перехода между **maxVal** и **minVal**.

Применяется там, где привод не умеет позиционироваться сам — например
коллекторный двигатель с внешним энкодером.''',
    topic_example='conductor_6/event/runUp',
    command_text={'action/currentPos': 'Текущая позиция — приходит от энкодера',
                  'action/targetPos': 'Целевая позиция'},
    report_example='Пример: топик `moduleBox/conductor_6/event/runUp`, payload `1`.',
    examples='''```ini
[SLOT_6]
mode = conductor
options = minVal:0, maxVal:1000, timeout:5000
;позиция от энкодера, команды движения - на выходы
crosslink = encoder_0/event/val:@->conductor_6/action/currentPos:@, conductor_6/event/runUp:1->out_1/action/ch_0:1, conductor_6/event/runDown:1->out_1/action/ch_1:1, conductor_6/event/stop:1->out_1/action/ch_0:0
```
Управление приводом с обратной связью от энкодера, таймаут 5 секунд.

```ini
[SLOT_7]
mode = conductor
options = minVal:0, maxVal:360, multiTurn:1
;поворотный стол на 360 позиций - модуль выбирает кратчайший путь
crosslink = encoder_0/event/val:@->conductor_7/action/currentPos:@
```''',
))

SPECS.append(dict(
    path=VIRT + 'tankControl_sw.md',
    manifest='tankControl',
    title='tankControl',
    tags=['sw', 'virtual', 'motor'],
    virtual=True,
    intro='Виртуальный модуль танкового микшера: смешивает «газ» и «руль» в скорости левой и правой гусениц.',
    principle='''Модуль принимает команды `accel` (газ) и `steering` (руль) и рассчитывает
скорости двух бортов, рапортуя их событиями `ch_0` (левый) и `ch_1` (правый).

Входные значения центрированы: середина диапазона **inputMinVal**–**inputMaxVal**
соответствует нулевой скорости. Опция **deadBand** задаёт мёртвую зону газа
вокруг центра, **outputMaxVal** ограничивает выходную скорость.

Применяется для гусеничных и колёсных машин с бортовым поворотом.''',
    topic_example='tankControl_6/event/ch_0',
    command_text={'action/accel': 'Газ — центрированное входное значение',
                  'action/steering': 'Руль — центрированное входное значение'},
    report_example='Пример: топик `moduleBox/tankControl_6/event/ch_0`, payload `180`.',
    examples='''```ini
[SLOT_6]
mode = tankControl
options = inputMinVal:0, inputMaxVal:255, outputMaxVal:255, deadBand:15
;два аналоговых входа - газ и руль, выходы - на драйверы бортов
crosslink = analog_0/event/rawVal:@->tankControl_6/action/accel:@, analog_1/event/rawVal:@->tankControl_6/action/steering:@
```
Мёртвая зона газа 15 единиц вокруг центра (128). События `ch_0` и `ch_1`
передают скорости левого и правого двигателей.''',
))

SPECS.append(dict(
    path=VIRT + 'watchdog_sw.md',
    manifest='watchdog',
    title='watchdog',
    tags=['sw', 'virtual'],
    virtual=True,
    intro='Виртуальный сторожевой таймер: перезагружает устройство, если его не сбрасывать.',
    principle='''При запуске модуль стартует отсчёт на **time** секунд. Команда `reset`
перезапускает отсчёт с начала. Если команда не приходит до истечения времени,
устройство перезагружается.

Применяется для автоматического восстановления после зависания или потери связи:
внешняя система периодически шлёт `reset`, и как только она перестаёт это делать,
устройство уходит в перезагрузку.

==У модуля нет событий: он не рапортует, а действует.==''',
    topic_example='watchdog_6/action/reset',
    examples='''```ini
[SLOT_6]
mode = watchdog
options = time:60
```
Сторожевой таймер на 60 секунд. Если за это время не придёт
`moduleBox/watchdog_6/action/reset`, устройство перезагрузится.

```ini
[SLOT_7]
mode = watchdog
options = time:300
;приход потока по сети сбрасывает сторожевой таймер
crosslink = audioStream_0/event/enable:1->watchdog_7/action/reset:1
```''',
))

# --------------------------------------------------------------- звук ----

PLAYER_COMPAT = [(HW + 'soundMono_hw', 'Модуль монофонического звука'),
                 (HW + 'soundStereo_hw', 'Модуль стереофонического звука'),
                 (HW + 'soundAmp_hw', 'Модуль усилителя мощности'),
                 (HW + 'SD_card', 'Модуль карты памяти')]

PLAYER_CMD_TEXT = {
    'action/play': 'Проиграть трек: номер, приращение `+N` / `-N`, `random` или `#` — текущий',
    'action/shift': 'Сдвинуть указатель трека без запуска воспроизведения',
    'action/stop': 'Остановить воспроизведение',
    'action/setVolume': 'Установить громкость',
}
PLAYER_CMD_PAYLOAD = {
    'action/play': 'целое, `+N` / `-N`, `random` или `#`',
    'action/shift': 'целое, `+N` / `-N` или `random`',
    'action/setVolume': '`0`–`100`',
}

for mid, title, fmt, tbl, extra_intro in [
    ('mp3Player', 'mp3Player', '.mp3',
     '''| Поддерживаемый формат | .mp3 |
| --- | --- |
| Битрейт | 192 kbps |
| Самплрейт | 44100 Гц |
| Количество каналов | 2 |''',
     'Есть возможность настроить тональность и скорость воспроизведения, а также эквалайзер в трёх диапазонах частот.'),
    ('wavPlayer', 'wavPlayer', '.wav',
     '''| Поддерживаемый формат | .wav |
| --- | --- |
| Самплрейт | 44100 Гц |
| Количество каналов | 2 |''',
     'Формат без сжатия — меньше нагрузка на процессор, больше объём файлов.'),
]:
    SPECS.append(dict(
        path=SOUND + mid + '_sw.md',
        manifest=mid,
        title=title,
        tags=['sw', 'sound', 'player'],
        intro='Программный модуль проигрывателя аудиофайлов формата %s. %s' % (fmt, extra_intro),
        compat=PLAYER_COMPAT,
        compat_note='==Модуль работает только в нулевом слоте.==',
        principle='''При запуске контроллер сканирует файловую систему, находит аудиофайлы формата
%s и сортирует их в алфавитном порядке. Дальше файлы проигрываются по номеру
в этом списке; по окончании трека модуль рапортует событие `endOfTrack`.

==Нумерация треков начинается с нуля.==

Опция **playToEnd** запрещает прерывать играющий трек новой командой, **playDelay**
добавляет паузу перед стартом, **attenuation** задаёт время плавного затухания
громкости при остановке.

%s''' % (fmt, tbl),
        topic_example='player_0/action/play',
        command_text=PLAYER_CMD_TEXT,
        command_payload=PLAYER_CMD_PAYLOAD,
        report_text={'event/endOfTrack': 'Номер трека, воспроизведение которого завершилось'},
        report_payload={'event/endOfTrack': 'целое'},
        report_example='Пример: топик `moduleBox/player_0/event/endOfTrack`, payload `2`.',
        command_example='Пример: топик `moduleBox/player_0/action/play`, payload `+1`.',
        examples='''```ini
[SLOT_0]
;модуль в режиме проигрывателя
mode = %s
;громкость 95%%, задержка перед стартом полсекунды
options = volume:95, playDelay:500
;по завершении любого трека проиграть следующий
crosslink = player_0/event/endOfTrack:#->player_0/action/play:+1
```
Спецсимволы `#` и `@` описаны на странице
[[Платформа moduleBox/CrossLink#Специальные символы|crossLink]].

```ini
[SLOT_0]
mode = %s
options = volume:80, playToEnd, attenuation:1500

[SLOT_1]
mode = button_led
;нажатие запускает случайный трек, длинное нажатие останавливает
crosslink = button_1/event/press:1->player_0/action/play:random, button_1/event/longPress:1->player_0/action/stop:1
```''' % (mid, mid),
    ))

LAN_COMPAT = [(HW + 'soundMono_hw', 'Модуль монофонического звука'),
              (HW + 'soundStereo_hw', 'Модуль стереофонического звука'),
              (HW + 'soundAmp_hw', 'Модуль усилителя мощности')]

LAN_INDICATION = '''- Светодиод **выключен** — модуль в состоянии DISABLE.
- Светодиод **горит постоянно** — модуль активен, поток принимается.
- Светодиод **мигает** — модуль активен, но поток не обнаружен.'''

SPECS.append(dict(
    path=SOUND + 'audioLAN_sw.md',
    manifest='audioLAN',
    title='audioLAN',
    tags=['sw', 'sound', 'lan'],
    intro='Программный модуль приёма и воспроизведения несжатого аудиопотока по локальной сети через RTP.',
    compat=LAN_COMPAT,
    compat_note='==Требуется подключение к локальной сети. Модуль работает только в нулевом слоте.==',
    principle='''Аудиопайплайн состоит из двух элементов: RTP-приёмник → I2S-выход. Декодирование
не выполняется — поток воспроизводится как есть.

Режим приёма определяется опцией **multicastAddress**: если адрес задан, модуль
подключается к multicast-группе, иначе принимает unicast-поток на порт **port**.
Адрес можно сменить на лету командой `setMulticastAddress`.

При запуске модуль ждёт инициализации сетевого интерфейса, затем стартует пайплайн
и рапортует своё состояние, громкость и адрес источника.

В отличие от [[Программные модули/Звуковые модули/opusLAN_sw|opusLAN]] поток идёт
без сжатия: задержка минимальна, но требуется заметно большая полоса пропускания.

| Параметр | Значение |
| --- | --- |
| Протокол | RTP (unicast / multicast) |
| Кодек | без сжатия (PCM) |
| Самплрейт | 48000 Гц (настраиваемый, 8000–96000) |
| Разрядность | 16 бит (настраиваемая, 8–32) |
| Каналы | 2 (стерео) |
| Задержка | ~70 мс |''',
    topic_example='audioStream_0/action/setVolume',
    report_example='Пример: топик `moduleBox/audioStream_0/event/volume`, payload `80`.',
    sections=[('Индикация', LAN_INDICATION)],
    examples='''```ini
[SLOT_0]
mode = audioLAN
options = multicastAddress:239.0.7.5, volume:80, port:7777

[SLOT_1]
mode = button_led
;нажатие ставит приём на паузу, отпускание возобновляет
crosslink = button_1/event/press:1->audioStream_0/action/enable:0, button_1/event/press:0->audioStream_0/action/enable:1
```''',
))

SPECS.append(dict(
    path=SOUND + 'opusLAN_sw.md',
    manifest='opusLAN',
    title='opusLAN',
    tags=['sw', 'sound', 'lan'],
    intro='Программный модуль приёма и воспроизведения аудиопотока по локальной сети через RTP с декодированием кодека Opus.',
    compat=LAN_COMPAT,
    compat_note='==Требуется подключение к локальной сети. Модуль работает только в нулевом слоте.==',
    principle='''Аудиопайплайн состоит из трёх элементов: RTP-приёмник → Opus-декодер → I2S-выход.

Режим приёма определяется опцией **multicastAddress**: если адрес задан, модуль
подключается к multicast-группе, иначе принимает unicast-поток на порт **port**.
Адрес можно сменить на лету командой `setMulticastAddress`.

Для синхронного воспроизведения на нескольких приёмниках модуль непрерывно
подстраивает тактовую частоту I2S под реальный самплрейт источника. Целевая
задержка синхронизации задаётся опцией **latencyMs** и ==должна быть одинаковой
на всех приёмниках==.

В отличие от [[Программные модули/Звуковые модули/audioLAN_sw|audioLAN]] поток
сжат кодеком Opus: требования к сети значительно ниже ценой чуть большей задержки.

| Параметр | Значение |
| --- | --- |
| Протокол | RTP (unicast / multicast) |
| Кодек | Opus |
| Самплрейт | 48000 Гц (настраиваемый, 8000–96000) |
| Разрядность | 16 бит (фиксированная) |
| Каналы | 2 (стерео) |
| Задержка | ~100 мс |''',
    topic_example='audioStream_0/action/setVolume',
    report_example='Пример: топик `moduleBox/audioStream_0/event/address`, payload `239.0.7.1`.',
    sections=[('Индикация', LAN_INDICATION)],
    examples='''```ini
[SLOT_0]
mode = opusLAN
options = multicastAddress:239.0.7.0, volume:100, latencyMs:50

[SLOT_1]
mode = button_led
;нажатие и отпускание переключают источник потока
crosslink = button_1/event/press:1->audioStream_0/action/setMulticastAddress:239.0.7.1, button_1/event/press:0->audioStream_0/action/setMulticastAddress:239.0.7.0
```''',
))

# ----------------------------------------------------------- служебные ----

SPECS.append(dict(
    path=SW + 'dialer_sw.md',
    manifest='dialer',
    title='dialer',
    tags=['sw', 'input'],
    intro='Программный модуль дискового телефонного номеронабирателя: считывает импульсы диска и собирает набранный номер.',
    compat=[(HW + 'in_2ch_hw', 'Модуль два цифровых входа'),
            (HW + 'in_3ch_hw', 'Модуль три цифровых входа')],
    principle='''Модуль читает два входных сигнала: один сообщает о начале набора цифры, второй
даёт импульсы, число которых равно набранной цифре. Каждый сигнал инвертируется
своим флагом — **enaInverse** и **pulseInverse**, дребезг механических контактов
подавляется опцией **debounceGap**.

Цифры накапливаются в строку и рапортуются событием `val`, когда набрано
**numberMaxLenght** цифр либо когда после последней цифры прошло **waitingTime**
миллисекунд. Незаконченный набор сбрасывается командой `reset`.''',
    topic_example='dialer_0/event/val',
    report_example='Пример: топик `moduleBox/dialer_0/event/val`, payload `1234567`.',
    sections=[('Пример подключения', '''![[Программные модули/_assets/dialer.svg]]

==В некоторых аппаратах может понадобиться дополнительная настройка модуля для
борьбы с дребезгом механических контактов: рекомендуется заменить конденсаторы
C1 и C2 на номинал 1 мкФ (по умолчанию 0.1 мкФ).==''')],
    examples='''```ini
[SLOT_0]
mode = dialer
options = numberMaxLenght:3, waitingTime:4000
;набранный номер уходит на проверку по списку
crosslink = dialer_0/event/val:@->whitelist_6/action/check:@

[SLOT_6]
mode = whitelist
options = filename:numbers.txt
```
Классический сценарий [[Устройства/retroTelephone|ретро-телефона]]: набранный
номер сверяется со списком, при совпадении проигрывается свой трек.''',
))

SPECS.append(dict(
    path=SW + 'dwin_sw.md',
    manifest='dwin',
    title='dwin',
    tags=['sw', 'uart', 'display'],
    intro='Программный модуль сенсорного дисплея DWIN по UART: читает изменения регистров VP и переключает страницы экрана.',
    compat=[(HW + 'uart_hw', 'Модуль интерфейса UART')],
    principle='''Модуль обменивается с дисплеем по протоколу DWIN. Изменения регистров VP,
которые дисплей шлёт при нажатии кнопок и вводе значений, публикуются событиями
вида `event/VP_xxxx`, где `xxxx` — адрес регистра в шестнадцатеричном виде.

Обратно на дисплей можно отправить команду смены страницы (`setPage`).

Набор регистров VP зависит от проекта, залитого в дисплей, поэтому в манифесте
модуля он не перечислен — конкретные адреса берутся из проекта дисплея.''',
    topic_example='dwin_0/action/setPage',
    report_example='Помимо `enable`, модуль публикует события по адресам регистров VP:\n\n'
                   '| Топик | Payload | Описание |\n|---|---|---|\n'
                   '| `dwin_<slot>/event/VP_xxxx` | целое | Новое значение регистра VP с адресом `xxxx` |\n\n'
                   'Пример: топик `moduleBox/dwin_0/event/VP_1000`, payload `3`.',
    examples='''```ini
[SLOT_2]
mode = dwin
;кнопка на экране (регистр VP 1000) запускает трек
crosslink = dwin_2/event/VP_1000:@->player_0/action/play:@

[SLOT_0]
mode = mp3Player
;по завершении трека вернуть дисплей на первую страницу
crosslink = player_0/event/endOfTrack:#->dwin_2/action/setPage:1
```''',
))

SPECS.append(dict(
    path=SW + 'testsd_sw.md',
    manifest='testsd',
    title='testsd',
    tags=['sw', 'service'],
    intro='Служебный модуль тестирования карты памяти: проверяет чтение и запись, рапортует прогресс и результат.',
    compat=[(HW + 'SD_card', 'Модуль карты памяти')],
    principle='''Модуль последовательно читает блоки карты, а в режимах `readwrite` и `readback`
дополнительно пишет их обратно и сверяет записанное. Тестирование запускается
командой `start` и прерывается командой `stop`.

Опция **maxErrors** задаёт число ошибок, после которого тест останавливается,
**runDelay** — паузу между блоками, чтобы тест не забирал всё процессорное время.

Модуль применяется при производственной проверке и диагностике носителей,
в рабочей конфигурации устройства он не нужен.''',
    topic_example='testsd_0/action/start',
    option_text={
        'testType': '*строка(enum)*, тип теста — см. [[#Типы теста]]. '
                    'Значения: `readwrite`, `read`, `readback`. По умолчанию `readwrite`.',
        'maxErrors': '*число(int)*, порог ошибок, после которого тестирование '
                     'останавливается. Диапазон 1–4096. По умолчанию 1.',
        'runDelay': '*число(int)*, пауза между чтением блоков в тиках FreeRTOS. '
                    'Диапазон 0–4096. По умолчанию 0.',
    },
    report_text={'event/state': 'Текущая фаза тестирования и детекция карты: `stopped`, `initializing`, `running`, `formatting`, `done`, `inserted`, `ejected`',
                 'event/result': 'Результат завершённого теста: `none`, `success`, `error`, `formatError`',
                 'event/progress': 'Прогресс тестирования в процентах'},
    report_payload={'event/progress': '`0`–`100`'},
    report_example='Пример: топик `moduleBox/testsd_0/event/progress`, payload `45`.',
    sections=[('Типы теста', '''
- **read** — только чтение блоков. Самый быстрый и безопасный: содержимое карты не меняется.
- **readwrite** — чтение и запись блока обратно. Проверяет, что карта принимает запись.
- **readback** — чтение, запись и проверка результата повторным чтением. Самый строгий и самый долгий.''')],
    examples='''```ini
[SLOT_1]
mode = testsd
options = testType:readback, maxErrors:5, runDelay:2
;кнопка запускает тест, результат уходит на подсветку
crosslink = button_0/event/press:1->testsd_1/action/start:1, testsd_1/event/result:success->led_0/action/enable:1
```
Режим `readback` — самый строгий: блок читается, записывается обратно и
проверяется повторным чтением. Тест останавливается после пяти ошибок.

```ini
[SLOT_1]
mode = testsd
options = testType:read, runDelay:5
;прогресс теста выводится шкалой на ленте
crosslink = testsd_1/event/progress:@->led_2/action/setPos:@
```''',
))
