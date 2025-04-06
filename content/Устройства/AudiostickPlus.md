---
title: Аудиоэтикетка+
draft: false
tags:
  - audio
  - device
---
![[Устройства/_assets/audioStickPlus.jpg]]
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
[SLOT_6] - [[Виртуальный слот]]
[[content/Программные модули/Виртуальные модули/startup_sw|Режим startup]]


## Схема подключения
![[Устройства/_assets/audioStickPlus.svg]]


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
В данном устройстве сетевые интерфейсы не используются, поэтому в конфигурационном файле пропущены группы: [LAN],[UDP],[OSC],[MQTT] подробнее [[Платформа moduleBox/Software#Структура конфигурационного файла|тут]].
Громкость проигрывания можно настроить как опцию *volume* в [SLOT_0].
Сигнал кнопки инвертирован в [SLOT_2], опцией *buttonInverse.*
[[Платформа moduleBox/Software#Внутренние связи(crossLink)|Crosslink]] в [SLOT_0] запускает повторное проигрывание текущего трека.
[[Платформа moduleBox/Software#Внутренние связи(crossLink)|Crosslink]] в [SLOT_2] запускает проигрывание нулевого трека при снятии динамика с базы, и останавливает при установке.
[[Платформа moduleBox/Software#Внутренние связи(crossLink)|Crosslink]] в [SLOT_3] при нажатии кнопки переводит указатель на трек с индексом 0, включает подсветку в слоте 3, и выключает в остальных.
[[Платформа moduleBox/Software#Внутренние связи(crossLink)|Crosslink]] в [SLOT_4] при нажатии кнопки переводит указатель на трек с индексом 1, включает подсветку в слоте 4, и выключает в остальных.
[[Платформа moduleBox/Software#Внутренние связи(crossLink)|Crosslink]] в [SLOT_5] при нажатии кнопки переводит указатель на трек с индексом 2, включает подсветку в слоте 5, и выключает в остальных.
Для первоначальной инициализации используется виртуальный слот [[Программные модули/Виртуальные модули/startup_sw|startup]].
[[Платформа moduleBox/Software#Внутренние связи(crossLink)|Crosslink]] в [SLOT_6] при старте устройства включает подсветку в слоте 3, и переводит указатель на трек с индексом 0.

