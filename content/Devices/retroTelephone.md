---
title: Ретро телефон
draft: false
tags:
  - "#device"
  - "#audio"
  - "#telephone"
---

#todo добавить изображение
## Описание
Устройство предназначено для проигрывания аудио контента, при снятии трубки с базы. Контент хранится на карте памяти внутри устройства. С помощью дискового номеронабирателя можно переключать звуковые дорожки. Файл связей, whitelist, располагается на карте памяти.

## Состав устройства

| Слот     | Аппаратный модуль                                                       | Программный модуль                                                      |
| -------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| (SLOT_0) | [[../Аппаратные модули/sound_mono_hw\|Модуль аудио моно]]               | [[content/Программные модули/audio_player_sw\|Аудио проигрыватель]]     |
| (SLOT_1) | [[SD_card]]                                                             | [[content/Платформа moduleBox/Software\|SDcard]]                        |
| (SLOT_2) | [[Аппаратные модули/buttonLed_hw\|Модуль кнопка с подсветкой]]          | [[content/Программные модули/buttonLed_sw\|Модуль кнопка с подсветкой]] |
| (SLOT_3) | [[content/Аппаратные модули/sensors_2ch_hw\|Модуль два цифровых входа]] | [[content/Программные модули/dialer_sw\|Дисковый номеронабиратель]]     |
| (SLOT_4) |                                                                         | [[content/Программные модули/whitelist_sw\|Белый список]]               |


## Схема подключения
![[content/Devices/_assets/retroPhone.svg]]


## Типовой конфиг
```ini
[SYSTEM] 
deviceName = retroTelephone 

[LAN] 
LAN_enable = 0 ;0-disable, 1-enable 
DHCP = 0 ;0-disable, 1-enable 
ipAdress = 192.168.88.33 
netMask = 255.255.255.0 
gateWay = 192.168.88.1 

[SLOT_0] 
mode = audio_player 
options = empty 
cross_link =  player_0/endOfTrack:#->player_0/play:# 
;по окончанию проигрывания, заново проиграть текущий трек

[SLOT_1] 
mode = SDcard 
options = empty 
cross_link = empty 

[SLOT_2] 
mode = button_led 
options = empty
cross_link = button_2:1->player_0/play:#, button_2:0->player_0/stop:#
;При снятии трубки начать прогрывание, при устновки трубки в телефон остановить проигрывание

[SLOT_3] 
mode = dialer 
options = numberMaxLenght:1 
;максимальная длина номера один символ
cross_link = dialer_3:@->whitelist_4:@
;передать набранный номер для проверки с белым списком

[SLOT_4] 
mode = whitelist
options = empty
;по умолчанию список хранится в корневом каталоге под именем whitelist.txt
cross_link = empty 
```
В данной конфигурации используются [[content/Платформа moduleBox/Software#Специальные символы|специальные символы]]

Пример списка [[content/Программные модули/whitelist_sw#Формат списка|whitelist.txt]]:
```ini
1->player_0/shift:0
2->player_0/shift:1
3->player_0/shift:2
```
Например: при наборе номера "1" указатель будет установлен на нулевой трек, если плеер запущен, нулевой трек будет проигран.