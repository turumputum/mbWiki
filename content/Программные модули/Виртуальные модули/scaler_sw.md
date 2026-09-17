---
title: scaler
draft: false
tags:
  - sw
  - virtual
---
```ini
[SLOT_n]
mode = scaler
```
Виртуальный модуль масштабирования: линейно приводит входное значение из одного диапазона в другой.

## Совместимость
Виртуальный модуль, аппаратной части не требует. Доступные слоты: 0-9.

## Принцип работы
Модуль принимает значение командой `pushInt` (целое) или `pushFloat`
(дробное), линейно пересчитывает его из диапазона **inputMinVal**–**inputMaxVal**
в диапазон **outputMinVal**–**outputMaxVal** и рапортует событием `result`.
Команда `pushVal` — устаревшее имя `pushInt`, оставлена для совместимости.

По умолчанию результат целый (округляется); флаг **floatOutput** сохраняет
дробную часть.

Опция **zeroDeadZone** задаёт мёртвую зону вокруг нуля — входные значения внутри
неё дают на выходе ноль. Это убирает дрожание около центра у джойстиков
и потенциометров.

## Топики
База топика события:
- `<deviceName>/scaler_<slot>` — например `moduleBox/scaler_0`

База топика действия:
- `<deviceName>/scaler_<slot>` — например `moduleBox/scaler_0`

Полный топик — база плюс направление и имя: `moduleBox/scaler_6/event/result`.

## Опции
Доступные опции:
- **disableOnStart** — *флаг*, стартовать в выключенном состоянии и ждать `action/enable` со значением `1`. По умолчанию модуль активен сразу.
- **zeroDeadZone** — *число(int)*, мертвая зона вокруг нуля. Диапазон 0–4096. По умолчанию 0.
- **inputMinVal** — *число(int)*, минимальное входное значение. По умолчанию 0.
- **inputMaxVal** — *число(int)*, максимальное входное значение. По умолчанию 255.
- **outputMinVal** — *число(int)*, минимальное выходное значение. По умолчанию 0.
- **outputMaxVal** — *число(int)*, максимальное выходное значение. По умолчанию 255.
- **intOutput** — *флаг*, отдавать результат целым числом (режим по умолчанию).
- **floatOutput** — *флаг*, отдавать результат с дробной частью. Если подняты оба флага — используется целый.

## События
| Топик | Payload | Описание |
|---|---|---|
| `scaler_<slot>/event/result` | целое, дробное при **floatOutput** | Масштабированное значение |
| `scaler_<slot>/event/enable` | `0` / `1` | Состояние модуля - активен 1 или спит 0 |

Пример: топик `moduleBox/scaler_6/event/result`, payload `128`.

## Команды
| Топик | Payload | Описание |
|---|---|---|
| `scaler_<slot>/action/pushInt` | целое | Входное значение, счёт в целых числах |
| `scaler_<slot>/action/pushFloat` | дробное | Входное значение, счёт с плавающей точкой |
| `scaler_<slot>/action/pushVal` | целое | То же, что `pushInt` (устаревшее имя) |
| `scaler_<slot>/action/enable` | `0` / `1` | Включить (`1`) или выключить (`0`) модуль |

## Примеры
```ini
[SLOT_6]
mode = scaler
options = inputMinVal:0, inputMaxVal:4095, outputMinVal:0, outputMaxVal:255
;значение аналогового входа приводится к диапазону яркости
crosslink = scaler_6/event/result:@->pwmLeds_1/action/setMaxBright:@
```
Значение АЦП 0–4095 приводится к 0–255. Источник подаёт значение командой
`scaler_6/action/pushInt`.

```ini
[SLOT_7]
mode = scaler
options = inputMinVal:0, inputMaxVal:255, outputMinVal:0, outputMaxVal:8000, zeroDeadZone:10
;позиция энкодера приводится к позиции шагового двигателя
crosslink = scaler_7/event/result:@->stepper_1/action/moveToAbs:@
```

Подробнее — [[Платформа moduleBox/CrossLink|внутренние связи (crossLink)]].
