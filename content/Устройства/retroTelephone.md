---
title: Ретро телефон
draft: false
tags:
  - "#device"
  - "#audio"
  - "#telephone"
---
![[Устройства/_assets/retroTel.jpg]]

## Описание
Устройство предназначено для проигрывания аудио контента, при снятии трубки с базы. Контент хранится на карте памяти внутри устройства. С помощью дискового номеронабирателя можно переключать звуковые дорожки. Файл связей, whitelist, располагается на карте памяти.

## Аппаратный состав устройства
- (SLOT_0) - [[Аппаратные модули/sound_mono_hw|Модуль аудио моно]]
- (SLOT_1) - [[Аппаратные модули/SD_card|SD_card]]
- (SLOT_2) - [[content/Аппаратные модули/button_led_hw|Модуль кнопка с подсветкой]]
- (SLOT_3) - [[Аппаратные модули/in_2ch_hw|Модуль два цифровых входа]]


## Программный состав устройства
- (SLOT_0) - [[content/Программные модули/mp3Player_sw|Аудио проигрыватель]]
- (SLOT_1) - [[Платформа moduleBox/Software|SDcard]]
- (SLOT_2) - [[content/Программные модули/button_led_sw|Модуль кнопка с подсветкой]]
- (SLOT_3) - [[Программные модули/dialer_sw|Дисковый номеронабиратель]]
- (SLOT_4) - [[Программные модули/Виртуальные модули/whitelist_sw|Белый список]]
## Схема подключения
![[Устройства/_assets/retroPhone.svg]]


## Типовой конфиг
```ini
[SYSTEM] 
deviceName = retroTelephone 

[SLOT_0] 
mode = mp3Player 
options = empty 
crosslink =  player_0/endOfTrack:#->player_0/play:# 
;по окончанию проигрывания, заново проиграть текущий трек

[SLOT_1] 
mode = SDcard 
options = empty 
crosslink = empty 

[SLOT_2] 
mode = button_led 
options = empty
crosslink = button_2:1->player_0/play:#, button_2:0->player_0/stop:#
;При снятии трубки начать прогрывание, при устновки трубки в телефон остановить проигрывание

[SLOT_3] 
mode = dialer 
options = numberMaxLenght:1 
;максимальная длина номера один символ
crosslink = dialer_3:@->whitelist_4:@
;передать набранный номер для проверки с белым списком

[SLOT_4] 
mode = whitelist
options = empty
;по умолчанию список хранится в корневом каталоге под именем whitelist.txt
crosslink = empty 
```
В данной конфигурации используются [[Платформа moduleBox/Software#Специальные символы|специальные символы]]

Пример списка [[Программные модули/Виртуальные модули/whitelist_sw#Формат списка|whitelist.txt]]:
```ini
1->player_0/shift:0
2->player_0/shift:1
3->player_0/shift:2
```
Например: при наборе номера "1" указатель будет установлен на нулевой трек, если плеер запущен(трубка снята), нулевой трек будет проигран.