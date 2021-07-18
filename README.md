# Что это?

Скрипт который проверяет и начинает запись стримов с твича (WIP)

# Как юзать?

* Поставить youtube-dl, python-twitch-client

`pip3 install python-twitch-client youtube-dl`

* Создать файл conf_python.py и добавить свой ключ (Можно получить на https://dev.twitch.tv/console), а также переменные: 

```
twitchid="ID" # ID ключа
streamers = ("jesusavgn", "252mart", "vi0xxx") # список стримеров в таком формате
path="/путь/до/диры/со/стримами" # путь до директории, куда писать стримы
```

* Добавить daemon.py в crontab, ну и офк убедиться что cron.service запущен (systemd timer не подойдет ибо он убивает child процессы после завершения работы родителя)

`*/5 * * * * /opt/twitch-downloader/cron.sh`

