# Bon Do
Охает, ахает, ухает, не любит украинский в опросах
Ругает за баяны (персистентно)

Живет [здесь](https://t.me/bon_do_bot)

Использует [форк](https://github.com/graynk/JImageHash/tree/database-chat) библиотеки [JImageHash](https://github.com/KilianB/JImageHash)

Можно запустить в докере:
```
export BOT_TOKEN=ваш_токен
docker run -d \
    --restart unless-stopped \
    --name bondo \
    -e BOT_TOKEN \
    --mount type=bind,source=./db,target=/root/db \
    graynk/bondo
```