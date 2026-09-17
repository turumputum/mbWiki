---
title: Аудиоэтикетка+ с подсветкой
draft: false
tags:
  - audio
  - device
---
*артикул 200-003*

![[Устройства/_assets/audioStickPlus_light.jpg]]
## Описание
[[Устройства/AudiostickPlus|Аудиоэтикетка+]] с подсвеченной магнитной базой: наушник на базе, три кнопки выбирают трек (например, язык), снятие наушника запускает выбранный трек, установка динамика в базу — останавливает. База подсвечена адресными светодиодами — цвет и анимация задаются в конфиге. Контент на карте памяти, сеть не нужна.

## Состав устройства
| Слот | Аппаратный модуль | Программный модуль |
|---|---|---|
| 0 | [soundMono](<Аппаратные модули/soundMono_hw.md>) — динамик 100-001 в наушнике | [mp3Player](<Программные модули/Звуковые модули/mp3Player_sw.md>) |
| 1 | [SD_card](<Аппаратные модули/SD_card_hw.md>) — карта памяти с треками | — |
| 2 | [button_smartLed](<Аппаратные модули/button_smartLed_hw.md>) через [miniDC-DC](<Аппаратные модули/miniDCDC_hw.md>) (201-038, 12 В → 5 В) — геркон магнитной базы 100-004 на `Bt`, подсветка базы 300-006 на `+5V`/`sLed` | [button_smartLed](<Программные модули/Кнопки с подсветкой/button_smartLed_sw.md>) |
| 3 | [button_led](<Аппаратные модули/button_led_hw.md>) — кнопка с подсветкой 300-001, трек 0 | [button_led](<Программные модули/Кнопки с подсветкой/button_led_sw.md>) |
| 4 | [button_led](<Аппаратные модули/button_led_hw.md>) — кнопка с подсветкой 300-001, трек 1 | [button_led](<Программные модули/Кнопки с подсветкой/button_led_sw.md>) |
| 5 | [button_led](<Аппаратные модули/button_led_hw.md>) — кнопка с подсветкой 300-001, трек 2 | [button_led](<Программные модули/Кнопки с подсветкой/button_led_sw.md>) |
| 6 | — (виртуальный) | [startup](<Программные модули/Виртуальные модули/startup_sw.md>) — начальное состояние |

Питание — блок питания 12 В MW RS-25-12 (артикул 201-007) на разъём Power.
Подсветка базы (WS2812) требует 5 В, поэтому на разъём модуля button_smartLed надет понижающий преобразователь [[Аппаратные модули/miniDCDC_hw|miniDC-DC]] (201-038): он даёт 5 В на `+5V`, а `sLed`, `Bt` и `gnd` пропускает насквозь.

## Схема подключения
![[Устройства/_assets/audioStickPlus_light.svg]]

База подключается четырьмя проводами к разъёму miniDC-DC на модуле button_smartLed: подсветка 300-006 — на `+5V`, `sLed`, `gnd`, геркон — на `Bt` и `gnd`. Каждая кнопка 300-001 — четырьмя проводами: светодиод на `led+`/`gnd`, контакт на `bt`/`gnd`.

## Типовой конфиг
```ini
[SYSTEM]
deviceName = audiostickPlusLight

[SLOT_0]
mode = mp3Player
options = volume:90

[SLOT_1]
mode = SD_card

;база: геркон и подсветка
[SLOT_2]
mode = button_smartLed
;геркон замкнут, пока наушник на базе: снятие даёт press = 1; цвет подсветки - синий
options = buttonInverse, RGBcolor:0 0 255
;снятие наушника - играть текущий трек, установка обратно - стоп
crosslink = button_2/event/press:1->player_0/action/play:#, button_2/event/press:0->player_0/action/stop:1

[SLOT_3]
mode = button_led
;выбрать трек 0: своя подсветка включается, остальные гаснут
crosslink = button_3/event/press:1->led_3/action/enable:1, button_3/event/press:1->led_4/action/enable:0, button_3/event/press:1->led_5/action/enable:0, button_3/event/press:1->player_0/action/shift:0

[SLOT_4]
mode = button_led
;выбрать трек 1
crosslink = button_4/event/press:1->led_4/action/enable:1, button_4/event/press:1->led_3/action/enable:0, button_4/event/press:1->led_5/action/enable:0, button_4/event/press:1->player_0/action/shift:1

[SLOT_5]
mode = button_led
;выбрать трек 2
crosslink = button_5/event/press:1->led_5/action/enable:1, button_5/event/press:1->led_3/action/enable:0, button_5/event/press:1->led_4/action/enable:0, button_5/event/press:1->player_0/action/shift:2

;виртуальный слот: начальное состояние при включении
[SLOT_6]
mode = startup
;при старте включить подсветку базы, выбрать трек 0 и зажечь первую кнопку
crosslink = startup_6/event/started:1->led_2/action/enable:1, startup_6/event/started:1->led_3/action/enable:1, startup_6/event/started:1->player_0/action/shift:0
```

- Сетевые интерфейсы не используются — группы `[LAN]`, `[UDP]`, `[OSC]`,
  `[MQTT]` в конфиге отсутствуют, см.
  [[Платформа moduleBox/Software#Структура конфигурационного файла|структуру конфигурационного файла]].
- Громкость — опция **volume** в `[SLOT_0]`.
- `[SLOT_2]`: **buttonInverse** — геркон замкнут, пока наушник на базе;
  `press` = `1` играет **текущий** трек (`#`), `press` = `0` останавливает.
  Подсветка базы настраивается опциями модуля
  [[Программные модули/Кнопки с подсветкой/button_smartLed_sw|button_smartLed]]:
  **RGBcolor**, **ledMode** (`flash`, `rainbow`), **numOfLed** — по числу
  светодиодов в подсветке 300-006.
- `[SLOT_3]`–`[SLOT_5]`: нажатие кнопки переводит указатель проигрывателя
  командой `shift` на трек 0 / 1 / 2, включает свою подсветку и гасит две
  другие.
- `[SLOT_6]`: [[Программные модули/Виртуальные модули/startup_sw|startup]]
  при включении зажигает подсветку базы, выбирает трек 0 и подсвечивает
  первую кнопку.

Подробнее — [[Платформа moduleBox/CrossLink|внутренние связи (crossLink)]].

## Архив
Описание устройства для прошивок до перехода на конституцию —
[[Архив/AudiostickPlus_light|Аудиоэтикетка+ с подсветкой (архив)]].
