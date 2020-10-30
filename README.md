# Bon Do
Охает, ахает, ухает, снова любит украинский в опросах

Говорит когда шаббат

## Использование

Живет [здесь](https://t.me/bon_do_bot)

## Сборка
Поставить Nim 1.4

```
nimble install telebot regex timezones
nim compile -d:ssl --opt:size -d:release bondo.nim
```
Проставить токен в переменную среды `BONDO_TOKEN`, ну и положить багет рядом с бинарником