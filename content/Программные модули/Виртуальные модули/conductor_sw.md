---
title: conductor
draft: false
tags:
  - sw
  - virtual
  - motor
---
```ini
[SLOT_n]
mode = conductor
```
Виртуальный модуль позиционирования: по текущей и целевой позиции выдаёт команды движения приводу.

## Совместимость
Виртуальный модуль, аппаратной части не требует. Доступные слоты: 0-9.

## Принцип работы
Модуль принимает текущую позицию от энкодера (`currentPos`) и целевую позицию
(`targetPos`). Он вычисляет направление движения и рапортует `runUp` или
`runDown`; по достижении цели либо по истечении **timeout** рапортует `stop`.

Флаг **multiTurn** включает многооборотную кинематику: модуль выбирает кратчайший
путь к цели через точку перехода между **maxVal** и **minVal**.

Применяется там, где привод не умеет позиционироваться сам — например
коллекторный двигатель с внешним энкодером.

## Топики
База топика события:
- `<deviceName>/conductor_<slot>` — например `moduleBox/conductor_0`

База топика действия:
- `<deviceName>/conductor_<slot>` — например `moduleBox/conductor_0`

Полный топик — база плюс направление и имя: `moduleBox/conductor_6/event/runUp`.

## Опции
Доступные опции:
- **disableOnStart** — *флаг*, стартовать в выключенном состоянии и ждать `action/enable` со значением `1`. По умолчанию модуль активен сразу.
- **minVal** — *число(int)*, минимальное значение позиции. По умолчанию 0.
- **maxVal** — *число(int)*, максимальное значение позиции. По умолчанию 32767.
- **multiTurn** — *число(int)*, многооборотная кинематика 0-1 по умолчанию 0. Диапазон 0–1. По умолчанию 0.
- **timeout** — *число(int)*, таймаут в миллисекундах (0 = без таймаута). По умолчанию 0.

## События
| Топик | Payload | Описание |
|---|---|---|
| `conductor_<slot>/event/stop` | строка | Отчёт остановки двигателя |
| `conductor_<slot>/event/runUp` | строка | Отчёт движения вверх |
| `conductor_<slot>/event/runDown` | строка | Отчёт движения вниз |
| `conductor_<slot>/event/enable` | `0` / `1` | Состояние модуля - активен 1 или спит 0 |

Пример: топик `moduleBox/conductor_6/event/runUp`, payload `1`.

## Команды
| Топик | Payload | Описание |
|---|---|---|
| `conductor_<slot>/action/currentPos` | целое | Текущая позиция — приходит от энкодера |
| `conductor_<slot>/action/targetPos` | целое | Целевая позиция |
| `conductor_<slot>/action/stop` | — | Остановить двигатель |
| `conductor_<slot>/action/enable` | `0` / `1` | Включить (`1`) или выключить (`0`) модуль |

## Примеры
```ini
[SLOT_6]
mode = conductor
options = minVal:0, maxVal:1000, timeout:5000
;позиция от энкодера, команды движения - на выходы
crosslink = encoder_0/event/val:@->conductor_6/action/currentPos:@, conductor_6/event/runUp:1->out_1/action/ch_0:1, conductor_6/event/runDown:1->out_1/action/ch_1:1, conductor_6/event/stop:1->out_1/action/ch_0:0
```
Управление приводом с обратной связью от энкодера, таймаут 5 секунд.

```ini
[SLOT_7]
mode = conductor
options = minVal:0, maxVal:360, multiTurn:1
;поворотный стол на 360 позиций - модуль выбирает кратчайший путь
crosslink = encoder_0/event/val:@->conductor_7/action/currentPos:@
```

Подробнее — [[Платформа moduleBox/CrossLink|внутренние связи (crossLink)]].
