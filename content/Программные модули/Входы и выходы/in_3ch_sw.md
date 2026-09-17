---
title: in_3ch
draft: false
tags:
  - sw
  - input
---
```ini
[SLOT_n]
mode = in_3ch
```
Программный модуль трёх цифровых входов с поддержкой логических операций над каналами.

## Совместимость
- [[Аппаратные модули/in_3ch_hw|Модуль три цифровых входа]]

## Принцип работы
Каналы опрашиваются с периодом **refreshPeriod**, дребезг контактов подавляется
опцией **inDebounceGap**. Каждый канал можно инвертировать флагом `inverse_N`.

Режим рапорта задаётся опцией **logic**:
- `independent` — каналы независимы, каждый рапортует своё состояние (`ch_0`, `ch_1`…);
- `or` — рапортуется `val` со значением `1`, если активен хотя бы один канал;
- `and` — рапортуется `val` со значением `1`, если активны все каналы.

## Топики
База топика события:
- `<deviceName>/in_<slot>` — например `moduleBox/in_0`

База топика действия:
- `<deviceName>/in_<slot>` — например `moduleBox/in_0`

Полный топик — база плюс направление и имя: `moduleBox/in_0/event/ch_0`.

## Опции
Доступные опции:
- **inverse_0** — *флаг*, инверсия сигнала на канале 0.
- **inverse_1** — *флаг*, инверсия сигнала на канале 1.
- **inverse_2** — *флаг*, инверсия сигнала на канале 2.
- **inDebounceGap** — *число(int)*, антидребезг в мс. Диапазон 1–4096. По умолчанию 10.
- **logic** — *строка(enum)*, логика каналов - independent or and. Значения: `independent`, `or`, `and`.
- **refreshPeriod** — *число(int)*, период опроса в мс. Диапазон 10–60000. По умолчанию 100.

## События
| Топик | Payload | Описание |
|---|---|---|
| `in_<slot>/event/ch_0` | целое | Состояние канала 0 |
| `in_<slot>/event/ch_1` | целое | Состояние канала 1 |
| `in_<slot>/event/ch_2` | целое | Состояние канала 2 |
| `in_<slot>/event/val` | целое | Комбинированное состояние каналов OR-AND |

Пример: топик `moduleBox/in_0/event/ch_2`, payload `1`.

В режиме `independent` рапортуются `ch_0`, `ch_1` и `ch_2`, в режимах `or` и `and` — `val`.

## Примеры
```ini
[SLOT_0]
mode = in_3ch
options = inDebounceGap:50, logic:independent
;три кнопки запускают три разных трека
crosslink = in_0/event/ch_0:1->player_0/action/play:0, in_0/event/ch_1:1->player_0/action/play:1, in_0/event/ch_2:1->player_0/action/play:2
```

```ini
[SLOT_1]
mode = in_3ch
options = logic:or, refreshPeriod:50
;срабатывание любого из трёх датчиков включает подсветку
crosslink = in_1/event/val:@->led_2/action/enable:@
```

Подробнее — [[Платформа moduleBox/CrossLink|внутренние связи (crossLink)]].
