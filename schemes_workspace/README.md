# schemes_workspace — схемы подключения контроллеров по проектам

```
schemes_workspace/
  <Проект>/
    <контроллер>/            # имя = deviceName из config.ini
      config.ini             # исходник: конфиг контроллера
      <deviceName>.scheme.yaml   # сгенерирован из config.ini, правится руками
      <deviceName>.svg       # схема
      <deviceName>.pdf       # схема для печати
```

Сборка (из корня репозитория):

```sh
python tools/scheme_gen/build.py "schemes_workspace/<Проект>/<контроллер>"
python tools/scheme_gen/build.py "schemes_workspace/<Проект>"          # все контроллеры
python tools/scheme_gen/build.py "<папка>" --force                    # YAML заново из config.ini
```

Как размечать `config.ini` (комментарии `;` внутри секций):

```ini
[SYSTEM]
;12v 100w mountPlate          <- БП 12V 100W под контроллером, монтажная плита
deviceName = mbw
boardVersion=4

[SLOT_0]
;servoStepper IHSV57 48V      <- сервопривод step/dir + драйвер IHSV57; 48V -> БП драйвера
mode = stepper

[SLOT_1]
; opticSensor_x2 BS5-T2M OCjumper   <- два датчика (ch_0, ch_1), перемычка OC на обоих каналах
mode = in_2ch

[SLOT_5]
;none                         <- модуль стоит, нагрузка не подключена
mode = relay

[SLOT_3]
; opticSensor G18-3A30NC solenoid   <- датчик на вход, соленоид на выход in_out
mode = in_out

[SLOT_4]
; servo 5V DCDC               <- рулевая машинка через DC-DC-«насадку» на слоте (12V -> 5V)
mode = PPMservo

[SLOT_5]
;hallSensor_x2 41F 'энкодер свитка'   <- в кавычках -> примечание под названием
mode = encoderInc
```

Без комментария берётся нагрузка по умолчанию для `mode`. Общий БП на
несколько драйверов, артикулы, цвета проводов — правкой `<deviceName>.scheme.yaml`
(см. `МИК/mbw` как образец: один `s0_psu` питает оба драйвера). Полный список типов,
флагов и пинов — `.claude/skills/connection-scheme/loads.yaml`; правила —
`tools/scheme_gen/README.md`.
