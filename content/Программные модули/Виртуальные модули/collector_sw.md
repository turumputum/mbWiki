---
title: Коллектор.
draft: false
tags:
  - "#trigger"
  - "#action"
  - "#sw"
  - "#virtualSlot"
---
```
[SLOT_n]
mode = collector
```
Виртуальный слот, не взаимодействует с аппаратной частью.

## Принцип работы
Модуль собирает в виде строки входящие символы. Рапортует при достижении заданной длины строки или по таймауту.
Применяется с кнопочным номеронабирателем.

## Топик
Стандартный топик событий и действий:
- *"deviceName/collector_{slot_num}"* - {slot_num} номер слота
	- пример: "moduleBox/collector_6"

## Опции
- **stringMaxLenght** - *(int)*, Максимальная длина строки. По умолчанию *7*.
- **waitingTime** - *(int)*, Время ожидания следующего символа. Единица измерения $мСек$. По умолчанию 3000 $мСек$ (3 секунды).
- **topic** - *строка*, нестандартный топик событий и действий.\

Пример
 ```ini
options= stringMaxLenght:5, waitingTime:1000
```

## Команды
- **/clear** - *(int)*, Очистка содержимого строки.
	- Пример: "*moduleBox/collector_3/clear*"
- **/add** - *(int)*, Добавление символов в строку.
	- Пример: "*moduleBox/collector_3/add:2*"

## Cобытия
При достижении заданной длины строки или времени ожидания, будет отрапортована собранная строка:
- *"moduleBox/collector_3:21233"* 

## Пример
```ini
[SLOT_0] 
mode = in_3ch 
options = inDebounceGap:50 
cross_link = in_0/ch_0:1->collector_3/add:r, in_0/ch_1:1->collector_3/add:C,in_0/ch_2:1->collector_3/add:D   

[SLOT_1] 
mode = in_3ch  
options = inDebounceGap:50 
cross_link = in_1/ch_1:1->collector_3/add:u, in_1/ch_0:1->collector_3/add:l, in_1/ch_2:1->collector_3/add:B  

[SLOT_2] 
mode = in_3ch  
options = inDebounceGap:50 
cross_link = in_2/ch_0:1->collector_3/add:d, in_2/ch_1:1->collector_3/add:A

[SLOT_3] 
mode = collector 
options = stringMaxLenght:5 
;Собранная строка передается в модуль "witelist" для валидации
cross_link = collector_3:@->whitelist_6:@
```

Подробнее об использовании [[Платформа moduleBox/Software#Внутренние связи(cross_link)|crossLink]]