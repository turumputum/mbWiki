---
title: Кнопки с подсветкой
draft: false
tags:
  - sw
  - button
  - led
---
Семейство программных модулей «кнопка + подсветка». Кнопочная часть у всех
одинаковая — те же опции и события; отличаются модули только подсветкой:
одноцветный светодиод, адресная лента, кольцо, шкала, бегущий эффект.

| Модуль | Подсветка | Аппаратный модуль |
|---|---|---|
| [button_led](<Программные модули/Кнопки с подсветкой/button_led_sw.md>) | одноцветный светодиод, плавная яркость, `flash` | [button_led](<Аппаратные модули/button_led_hw.md>), [in_out](<Аппаратные модули/in_out_hw.md>) |
| [button_smartLed](<Программные модули/Кнопки с подсветкой/button_smartLed_sw.md>) | адресная лента одним цветом, `flash` / `rainbow` | [button_smartLed](<Аппаратные модули/button_smartLed_hw.md>) |
| [button_ledRing](<Программные модули/Кнопки с подсветкой/button_ledRing_sw.md>) | кольцо: пятно в позиции или бегущее | [button_smartLed](<Аппаратные модули/button_smartLed_hw.md>) |
| [button_ledBar](<Программные модули/Кнопки с подсветкой/button_ledBar_sw.md>) | шкала заполнения до заданной позиции | [button_smartLed](<Аппаратные модули/button_smartLed_hw.md>) |
| [button_runFire](<Программные модули/Кнопки с подсветкой/button_runFire_sw.md>) | бегущий световой эффект по ленте | [button_smartLed](<Аппаратные модули/button_smartLed_hw.md>) |
| [button_swiperLed](<Программные модули/Кнопки с подсветкой/button_swiperLed_sw.md>) | эффект свайпа в четырёх направлениях | [button_smartLed](<Аппаратные модули/button_smartLed_hw.md>) |

## Общая кнопочная часть
База топика события — `<deviceName>/button_<slot>`, команд подсветки —
`<deviceName>/led_<slot>`. Автоматизация на событиях кнопки переносится между
модулями без правок.

Опции кнопки: **buttonInverse**, **buttonDebounceGap**, **longPressTime**,
**doubleClickTime**, **eventFilter**, **switchModeButton**.

| Событие | Когда |
|---|---|
| `button_<slot>/event/press` | нажатие `1` / отпускание `0` |
| `button_<slot>/event/longPress` | удержание дольше **longPressTime** |
| `button_<slot>/event/doubleClick` | два нажатия в пределах **doubleClickTime** |
| `button_<slot>/event/switch` | режим переключателя (**switchModeButton**): каждое нажатие меняет `0`/`1`, `press` не шлётся |

У подсветки всегда есть `action/toggleLedState` и `action/enable`; остальные
команды (`setRGB`, `setPos`, `setMode`, `swipe`, …) зависят от модуля.

## Пример
```ini
[SLOT_1]
mode = button_smartLed
options = RGBcolor:0 0 255, switchModeButton
;кнопка-переключатель: своё состояние - в собственную подсветку
crosslink = button_1/event/switch:@->led_1/action/enable:@
```
Нажатие включает подсветку, следующее — выключает. Заменив `mode` на
`button_led` или `button_ledRing`, получаем то же поведение с другой
подсветкой.

Подробнее — [[Платформа moduleBox/CrossLink|внутренние связи (crossLink)]].
