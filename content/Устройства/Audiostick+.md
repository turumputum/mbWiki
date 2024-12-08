---
title: Аудиоэтикетка+ с подсветкой
draft: false
tags:
  - audio
  - device
---
![[Устройства/_assets/audioStick+.jpg]]
>[!info]- be
>![[content/Устройства/_assets/lejaflorezt.gif]]

## Описание
Устройство предназначено для проигрывания аудио контента, при снятии наушника с базы. C помощью кнопок может быть настроено переключение контента, например для смены языка.

## Состав устройства
- [SLOT_0] - [[Аппаратные модули/sound_mono_hw|Модуль аудио моно]]
[[Программные модули/audio_player_sw|Режим audioPlayer]]
- [SLOT_1] - [[Аппаратные модули/SD_card|Модуль карты памяти]]
- [SLOT_2] - [[Аппаратные модули/buttonLed_hw|Модуль кнопка с подсветкой]]
[[Программные модули/buttonLed_sw|Режим кнопка с подсветкой]]


## Схема подключения
![[content/Устройства/_assets/audioStick+_light.svg]]


## Типовой конфиг
```ini
[SYSTEM] 
deviceName = audiostick 

[LAN] 
LAN_enable = 0 ;0-disable, 1-enable 
DHCP = 0 ;0-disable, 1-enable 
ipAdress = 192.168.88.33 
netMask = 255.255.255.0 
gateWay = 192.168.88.1 

[SLOT_0] 
mode = audioPlayer 
options = empty
cross_link = empty 

[SLOT_1] 
mode = SD_card
options = empty 
cross_link = empty 

[SLOT_2] 
mode = button_led
options = empty 
cross_link = button_2:1->player_0/play:0, button_2:0->player_0/stop 

```