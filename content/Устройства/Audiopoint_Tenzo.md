---
title: Аудиоточка с тензодатчиками
draft: false
tags:
  - audio
  - device
  - tenzo
  - radar
---
#to-do Изображение

## Описание
Устройство предназначено для проигрывания аудио контента при детекции посетителя датчиком присутствия. C помощью тензо кнопок может быть настроено переключение контента, например для смены языка. В качестве динамика используется пассивный 

## Состав устройства
- [SLOT_0] - [[Аппаратные модули/sound_amp_hw|Модуль аудио с усилителем]]
[[content/Программные модули/Звуковые модули/mp3Player_sw|Режим mp3Player]]
- [SLOT_1] - [[Аппаратные модули/SD_card|Модуль карты памяти]]
- [SLOT_2] - [[Аппаратные модули/tenzoButton_hw|Модуль тензо кнопка]]
[[Программные модули/tenzoButton_sw|Режим тензо кнопка]]
- [SLOT_3] - [[Аппаратные модули/tenzoButton_hw|Модуль тензо кнопка]]
[[Программные модули/tenzoButton_sw|Режим тензо кнопка]]
- [SLOT_4] - [[Аппаратные модули/out_2ch_hw|Модуль два цифровых выхода]]
[[Программные модули/out_2ch_sw|Режим два цифровых выхода]]
- [SLOT_5] - [[Аппаратные модули/uart_hw|Модуль UART интерфейса]]
[[Программные модули/hlk2410_sw|Режим датчика HLK2410]]


## Схема подключения
![[Устройства/_assets/audioPoint_tenzo.svg]]


## Типовой конфиг
```ini
[SYSTEM] 
deviceName = audiopointTenzo 

[SLOT_0] 
mode = mp3Player 
options = attenuation
;настроено плавное затухание громкости по команде стоп
crosslink = player_0/endOfTrack:0->out_4/ch_0:1, player_0/endOfTrack:0->out_4/ch_1:1 
;по окончанию проигрывания трека, нулевой и первый каналы выходного модуля в четвертом слоте устанавливаются в активное состояние

[SLOT_1] 
mode = SDcard 
options = empty 
crosslink = empty 

[SLOT_2] 
mode = tenzoButton 
options = boolean
;дискретный режим работы модуля
crosslink = tenzoButton_2:1->player_0/play:1, tenzoButton_2:1->out_4/ch_0:1, tenzoButton_2:1->out_4/ch_1:0 
;при наажатии на тензо кнопку подключенную к слоту два, запускается трек с индексом один, включается нулевой канал, и выключается первый канал в слоте четыре

[SLOT_3] 
mode = tenzoButton 
options = boolean 
crosslink = tenzoButton_3:1->player_0/play:2, tenzoButton_3:1->out_4/ch_0:0, tenzoButton_3:1->out_4/ch_1:1
;при наажатии на тензо кнопку подключенную к слоту три, запускается трек с индексом два, выключается нулевой канал, и включается первый канал в слоте четыре

[SLOT_4] 
mode = out_3ch 
options = empty 
crosslink = empty 

[SLOT_5] 
mode = hlk2410 
options = threshold:140, filterK:0.05, cooldownTime:5000, maxVal:200
;модуль радара настроен как дискретный выход, с порогом срабатывания в 140см, и высокой степенью сглаживания сигнала
crosslink = distanceSens_5/threshold:1->out_4/ch_0:1, distanceSens_5/threshold:1->out_4/ch_1:1, distanceSens_5/threshold:1->player_0/play:0, distanceSens_5/threshold:1->timer_6/stop, distanceSens_3/threshold:0->timer_6/start:3000
;при активации датчика нулевой и первый каналы выходного модуля в четвертом слоте устанавливаются в активное состояние, запускается проигрывание трека с индексом ноль и останавливается виртуальный таймер в шестом слоте.
;при деактивации датчика запускается таймер в шестом слоте

[SLOT_6] 
;виртуальный слот
mode = timer 
options = empty 
crosslink = timer_6/timerEnd->player_0/stop, timer_6/timerEnd->out_4/ch_0:0, timer_6/timerEnd->out_4/ch_1:0
;при достижении целевого значения таймера, проигрыватель, а также нулевой и первый каналы четвертого слота будут деактивированы  
```




