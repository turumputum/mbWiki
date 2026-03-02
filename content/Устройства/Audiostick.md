---
title: Аудиоэтикетка
draft: false
tags:
  - audio
  - device
---
*артикул 200-001*


![[Устройства/_assets/audioStick.jpg]]
## Описание
Устройство предназначено для проигрывания аудио контента, при снятии наушника с базы.

## Состав устройства
- [SLOT_0] - [[Аппаратные модули/soundMono_hw|Модуль аудио моно]]
[[Программные модули/Звуковые модули/mp3Player_sw|Режим mp3Player]]
- [SLOT_1] - [[Аппаратные модули/SD_card|Модуль карты памяти]]
- [SLOT_2] - [[Аппаратные модули/button_led_hw|Модуль кнопка с подсветкой]]
[[Программные модули/button_led_sw|Режим кнопка с подсветкой]]


## Схема подключения
![[Устройства/_assets/audioStick.svg]]


## Типовой конфиг
```ini
[SYSTEM] 
deviceName = audiostick 

[SLOT_0] 
mode = mp3Player 
options = volume:75
crosslink = player_0/endOfTrack:#->player_0/play:# 

[SLOT_1] 
mode = SD_card
options = empty 
crosslink = empty 

[SLOT_2] 
mode = button_led
options = buttonInverse 
crosslink = button_2:1->player_0/play:0, button_2:0->player_0/stop 
```
В данном устройстве сетевые интерфейсы не используются, поэтому в конфигурационном файле пропущены группы: [LAN],[UDP],[OSC],[MQTT] подробнее [[Платформа moduleBox/Software#Структура конфигурационного файла|тут]].
Громкость проигрывания можно настроить как опцию *volume* в [SLOT_0].
Сигнал кнопки инвертирован в [SLOT_2], опцией *buttonInverse.*
[[Платформа moduleBox/Software#Внутренние связи(crossLink)|Crosslink]] в [SLOT_0], запускает повторное проигрывание текущего трека.
[[Платформа moduleBox/Software#Внутренние связи(crossLink)|Crosslink]] в [SLOT_2] запускает проигрывание нулевого трека при снятии динамика с базы, и останавливает при установке.