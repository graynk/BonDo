# Bon Do
Охает, ахает, ухает, говорит когда шаббат и когда шабака

## Использование

Живет [здесь](https://t.me/bon_do_bot)

## Сборка
Можно запустить в докере:

```
export BOT_TOKEN=ваш_токен
docker run -d \
    --restart unless-stopped \
    --name bondo \
    -e BOT_TOKEN \
    -v /path/to/gpt/models:/usr/app/models \
    ghcr.io/graynk/bondobot
```
