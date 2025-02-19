---
title: Аудиоэтикетка+ с подсветкой
draft: false
tags:
  - audio
  - device
---
![[Устройства/_assets/audioStickPlus_light.jpg]]
## Описание
Устройство предназначено для проигрывания аудио контента, при снятии наушника с базы. C помощью кнопок может быть настроено переключение контента, например для смены языка.

## Состав устройства
- [SLOT_0] - [[Аппаратные модули/sound_mono_hw|Модуль аудио моно]]
[[Программные модули/audio_player_sw|Режим audioPlayer]]
- [SLOT_1] - [[Аппаратные модули/SD_card|Модуль карты памяти]]
- [SLOT_2] - [[Аппаратные модули/button_smartLed_hw|Модуль кнопка с управляемой подсветкой]]
[[Программные модули/buttonLed_sw|Режим кнопка с управляемой подсветкой]]
- [SLOT_3] - [[Аппаратные модули/buttonLed_hw|Модуль кнопка с подсветкой]]
[[Программные модули/buttonLed_sw|Режим кнопка с подсветкой]]
- [SLOT_4] - [[Аппаратные модули/buttonLed_hw|Модуль кнопка с подсветкой]]
[[Программные модули/buttonLed_sw|Режим кнопка с подсветкой]]
- [SLOT_5] - [[Аппаратные модули/buttonLed_hw|Модуль кнопка с подсветкой]]
[[Программные модули/buttonLed_sw|Режим кнопка с подсветкой]]


## Схема подключения
![[Устройства/_assets/audioStickPlus_light.svg]]


## Типовой конфиг
```ini
[SYSTEM] 
deviceName = audiostickPlus 

[SLOT_0] 
mode = audioPlayer
options = volume:0.9 
cross_link = empty 

[SLOT_1] 
mode = SD_card 
options = empty 
cross_link = empty 

;слот отслеживает положения динамика в базе, и управляет подсветой базы
[SLOT_2] 
mode = button_smartLed 
options = buttonInverse
cross_link = button_2:1->player_0/play:#, button_2:0->player_0/stop:#

[SLOT_3] 
mode = button_led 
options = empty 
cross_link = button_3:1->led_3:1, button_3:1->led_4:0, button_3:1->led_5:0, button_3:1->player_0/shift:0 

[SLOT_4] 
mode = button_led 
options = empty 
cross_link = button_4:1->led_4:1, button_4:1->led_3:0, button_4:1->led_5:0, button_4:1->player_0/shift:1  

[SLOT_5] 
mode = button_led 
options = empty 
cross_link = button_5:1->led_5:1, button_5:1->led_3:0, button_5:1->led_4:0, button_5:1->player_0/shift:2 

;виртуальный слот, для настроки устройтва при включении
[SLOT_6] 
mode = startup 
options = empty 
cross_link = startup->led_3:1, sturtup->player_0/shift:0 

```




