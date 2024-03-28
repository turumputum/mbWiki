---
title: Аудиоэтикетка
draft: false
tags:
---
*артикул 200-001*


#todo добавить изображение
## Описание
Устройство предназначено для проигрывания аудио контента, при снятии наушника с базы.

## Состав устройства
- [SLOT_0] - [[Аппаратные модули/audio_player_mono_hw|Модуль аудио моно]]
[[Программные модули/audio_player_sw|Режим audio_player]]
- [SLOT_1] - [[Аппаратные модули/SD_card]]
- [SLOT_2] - [[Аппаратные модули/buttonLed_hw|Программные модули/Модуль кнопка с подсветкой]]
[[Программные модули/buttonLed_sw|Режим button_led]]


## Схема подключения
![[audioStick.svg]]


## Типовой конфиг
```ini
;config file moduleBox. Ver:3.20 

[SYSTEM] 
device_name = audiostick 

[LAN] 
LAN_enable = 0 ;0-disable, 1-enable 
DHCP = 0 ;0-disable, 1-enable 
ipAdress = 192.168.88.33 
netMask = 255.255.255.0 
gateWay = 192.168.88.1 

[SLOT_0] 
mode = audio_player 
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

[SLOT_3] 
mode = empty 
options = empty 
cross_link = empty 

[SLOT_4] 
mode = empty 
options = empty 
cross_link = empty 

[SLOT_5] 
mode = empty 
options = empty 
cross_link = empty 

```