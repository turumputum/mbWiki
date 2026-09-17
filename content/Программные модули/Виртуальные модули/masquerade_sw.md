---
title: masquerade
draft: false
tags:
  - sw
  - virtual
---
```ini
[SLOT_n]
mode = masquerade
```
Виртуальный модуль-ретранслятор: перенаправляет входящие значения в другой, «замаскированный» топик.

## Совместимость
Виртуальный модуль, аппаратной части не требует. Доступные слоты: 0-9.

## Принцип работы
Значение, поступившее командой `push`, публикуется в топик, заданный опцией
**mask**. Применяется для переименования топиков, маршрутизации сообщений между
устройствами и агрегации событий разных модулей в один поток.

==База топика действия (`masquerade_<slot>`) и база топика события
(`masq_<slot>`) у этого модуля различаются.==

## Топики
База топика события:
- `<deviceName>/masq_<slot>` — например `moduleBox/masq_0`

База топика действия:
- `<deviceName>/masquerade_<slot>` — например `moduleBox/masquerade_0`

Полный топик — база плюс направление и имя: `moduleBox/masquerade_6/action/push`.

## Опции
Доступные опции:
- **mask** — *строка*, выходной замаскированный топик (база-маска). По умолчанию /masq_0.

## События
| Топик | Payload | Описание |
|---|---|---|
| `masq_<slot>/event/val` | строка | Отчёт значения в выходной топик |
| `masq_<slot>/event/enable` | `0` / `1` | Состояние модуля - активен 1 или спит 0 |

Пример: топик `moduleBox/masq_6/event/val`, payload `1`.

## Команды
| Топик | Payload | Описание |
|---|---|---|
| `masquerade_<slot>/action/push` | строка | Передать значение в замаскированный топик |
| `masquerade_<slot>/action/enable` | `0` / `1` | Включить (`1`) или выключить (`0`) модуль |

## Примеры
```ini
[SLOT_6]
mode = masquerade
options = mask:zone_1/trigger
;нажатие кнопки уходит во внешний топик zone_1/trigger
crosslink = button_0/event/press:@->masquerade_6/action/push:@
```

```ini
[SLOT_7]
mode = masquerade
options = mask:player_control/play
;события двух разных датчиков сводятся в один топик
crosslink = distanceSens_1/event/threshold:1->masquerade_7/action/push:1, tenzoButton_2/event/val:1->masquerade_7/action/push:1
```

Подробнее — [[Платформа moduleBox/CrossLink|внутренние связи (crossLink)]].
