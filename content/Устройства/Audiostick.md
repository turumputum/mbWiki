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
- [SLOT_0] - [[Аппаратные модули/sound_mono_hw|Модуль аудио моно]]
[[Программные модули/audio_player_sw|Режим audioPlayer]]
- [SLOT_1] - [[Аппаратные модули/SD_card|Модуль карты памяти]]
- [SLOT_2] - [[Аппаратные модули/buttonLed_hw|Модуль кнопка с подсветкой]]
[[Программные модули/buttonLed_sw|Режим кнопка с подсветкой]]


## Схема подключения
![[Устройства/_assets/audioStick.svg]]


## Типовой конфиг
```ini
[SYSTEM] 
deviceName = audiostick 

[SLOT_0] 
mode = audioPlayer 
options = volume:0.75
cross_link = player_0/endOfTrack:#->player_0/play:# 

[SLOT_1] 
mode = SD_card
options = empty 
cross_link = empty 

[SLOT_2] 
mode = button_led
options = buttonInverse 
cross_link = button_2:1->player_0/play:0, button_2:0->player_0/stop 
```
В данном устройстве сетевые интерфейсы не используются, поэтому в конфигурационном файле пропущены группы: [LAN],[UDP],[OSC],[MQTT] подробнее [[content/Платформа moduleBox/Software#Структура конфигурационного файла|тут]].
Громкость проигрывания можно настроить как опцию *volume* в [SLOT_0].
Сигнал кнопки инвертирован в [SLOT_2], опцией *buttonInverse.*
[[content/Платформа moduleBox/Software#Внутренние связи(crossLink)|Crosslink]] в [SLOT_0], запускает повторное проигрывание текущего трека.
[[content/Платформа moduleBox/Software#Внутренние связи(crossLink)|Crosslink]] в [SLOT_2] запускает проигрывание нулевого трека при снятии динамика с базы, и останавливает при установке.