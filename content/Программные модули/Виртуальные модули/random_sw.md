---
title: random
draft: false
tags:
  - sw
  - virtual
---
```ini
[SLOT_n]
mode = random
```
Виртуальный модуль генератора случайных чисел.

## Совместимость
Виртуальный модуль, аппаратной части не требует. Доступные слоты: 0-9.

## Принцип работы
По команде `generate` модуль выдаёт случайное целое число и рапортует его.
Диапазон определяется параметром команды:
- без параметра — диапазон из опций **minVal**–**maxVal**;
- одно число `N` — диапазон от 0 до `N`;
- два числа через пробел — указанный диапазон.

## Топики
База топика события:
- `<deviceName>/random_<slot>` — например `moduleBox/random_0`

База топика действия:
- `<deviceName>/random_<slot>` — например `moduleBox/random_0`

Полный топик — база плюс направление и имя: `moduleBox/random_6/event/val`.

## Опции
Доступные опции:
- **disableOnStart** — *флаг*, стартовать в выключенном состоянии и ждать `action/enable` со значением `1`. По умолчанию модуль активен сразу.
- **maxVal** — *число(int)*, верхняя граница диапазона генерации. По умолчанию максимум int32.
- **minVal** — *число(int)*, нижняя граница диапазона генерации. По умолчанию 0.

## События
| Топик | Payload | Описание |
|---|---|---|
| `random_<slot>/event/val` | целое | Возвращает сгенерированное значение |
| `random_<slot>/event/enable` | `0` / `1` | Состояние модуля - активен 1 или спит 0 |

Пример: топик `moduleBox/random_6/event/val`, payload `7`.

## Команды
| Топик | Payload | Описание |
|---|---|---|
| `random_<slot>/action/generate` | — либо `N` / `N M` | Сгенерировать число. Без параметра - в диапазоне minVal-maxVal из опций; одно число N - в диапазоне 0-N; два числа через пробел - в этом диапазоне |
| `random_<slot>/action/enable` | `0` / `1` | Включить (`1`) или выключить (`0`) модуль |

## Примеры
```ini
[SLOT_6]
mode = random
options = minVal:1, maxVal:10
;нажатие кнопки генерирует число от 1 до 10
crosslink = button_0/event/press:1->random_6/action/generate:1
```

```ini
[SLOT_7]
mode = random
options = minVal:0, maxVal:5
;случайное число используется как индекс трека
crosslink = button_0/event/press:1->random_7/action/generate:1, random_7/event/val:@->player_0/action/play:@
```

Подробнее — [[Платформа moduleBox/CrossLink|внутренние связи (crossLink)]].
