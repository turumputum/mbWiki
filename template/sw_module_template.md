---
title: Энкодер ШИМ
draft: false
tags:
---
```
[SLOT_n]
mode = button_led
```
## Описание

## Совместимость

## Принцип работы

## Топики
Стандартный топик события:
- *"device_name/encoder_{slot_num}"* - {slot_num} номер слота
	- пример: "module_box/encoder_0"
Стандартный топик действия:

## Опции
Доступные опции:
- **absolute** - *флаг*, абсолютный режим работы энкодера	


## Примеры
Пример настройки подсветки:
```
options = absolute, float_output, encoder_topic:/volume
```
В топик "/volume" будет публиковаться текущее положение энкодера виде числа от 0,0 до 1,0 с плавающей точкой.


Пример использование [[cross_link]]:
```
cross_link = button_0:1->led_0:1; turn on led_0 when button_0 is pressed
```

