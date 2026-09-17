---
title: Аудиоэтикетка+
draft: false
tags:
  - audio
  - device
---
*артикул 200-002*

![[Устройства/_assets/audioStickPlus.jpg]]
## Описание
Аудиоэтикетка с выбором контента: наушник на магнитной базе и три кнопки с
подсветкой. Кнопки выбирают трек — например язык экскурсии, — подсветка
показывает текущий выбор; снятие наушника запускает выбранный трек,
установка на базу — останавливает. Контент на карте памяти, сеть не нужна.

## Состав устройства
| Слот | Аппаратный модуль | Программный модуль |
|---|---|---|
| 0 | [soundMono](<Аппаратные модули/soundMono_hw.md>) — динамик 100-001 в наушнике | [mp3Player](<Программные модули/Звуковые модули/mp3Player_sw.md>) |
| 1 | [SD_card](<Аппаратные модули/SD_card_hw.md>) — карта памяти с треками | — |
| 2 | [button_smartLed](<Аппаратные модули/button_smartLed_hw.md>) — вход `Bt`: геркон магнитной базы 100-004 | [button_smartLed](<Программные модули/Кнопки с подсветкой/button_smartLed_sw.md>) |
| 3 | [button_led](<Аппаратные модули/button_led_hw.md>) — кнопка с подсветкой 300-001, трек 0 | [button_led](<Программные модули/Кнопки с подсветкой/button_led_sw.md>) |
| 4 | [button_led](<Аппаратные модули/button_led_hw.md>) — кнопка с подсветкой 300-001, трек 1 | [button_led](<Программные модули/Кнопки с подсветкой/button_led_sw.md>) |
| 5 | [button_led](<Аппаратные модули/button_led_hw.md>) — кнопка с подсветкой 300-001, трек 2 | [button_led](<Программные модули/Кнопки с подсветкой/button_led_sw.md>) |
| 6 | — (виртуальный) | [startup](<Программные модули/Виртуальные модули/startup_sw.md>) — начальное состояние |

Питание — блок питания 12 В MW RS-25-12 (артикул 201-007) на разъём Power.

## Схема подключения
![[Устройства/_assets/audioStickPlus.svg]]

Геркон базы — сухой контакт между `Bt` и `gnd` модуля button_smartLed
(лента подсветки не подключается). Каждая кнопка 300-001 — четырьмя проводами:
светодиод на `led+`/`gnd`, контакт на `bt`/`gnd`.

## Типовой конфиг
```ini
[SYSTEM]
deviceName = audiostickPlus

[SLOT_0]
mode = mp3Player
options = volume:90

[SLOT_1]
mode = SD_card

[SLOT_2]
mode = button_smartLed
;геркон замкнут, пока наушник на базе: снятие даёт press = 1
options = buttonInverse
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
;при старте выбран трек 0 и горит первая кнопка
crosslink = startup_6/event/started:1->led_3/action/enable:1, startup_6/event/started:1->player_0/action/shift:0
```

- Сетевые интерфейсы не используются — группы `[LAN]`, `[UDP]`, `[OSC]`,
  `[MQTT]` в конфиге отсутствуют, см.
  [[Платформа moduleBox/Software#Структура конфигурационного файла|структуру конфигурационного файла]].
- Громкость — опция **volume** в `[SLOT_0]`.
- `[SLOT_2]`: геркон замкнут, пока наушник на базе, поэтому **buttonInverse**;
  `press` = `1` играет **текущий** трек (`#`, см.
  [[Платформа moduleBox/CrossLink#Специальные символы|специальные символы]]),
  `press` = `0` останавливает.
- `[SLOT_3]`–`[SLOT_5]`: нажатие кнопки переводит указатель проигрывателя
  командой `shift` на трек 0 / 1 / 2 без запуска воспроизведения, включает
  свою подсветку и гасит две другие.
- `[SLOT_6]`: [[Программные модули/Виртуальные модули/startup_sw|startup]]
  при включении выставляет исходное состояние — выбран трек 0, горит первая
  кнопка.

Подробнее — [[Платформа moduleBox/CrossLink|внутренние связи (crossLink)]].

## Архив
Описание устройства для прошивок до перехода на конституцию —
[[Архив/AudiostickPlus|Аудиоэтикетка+ (архив)]].
