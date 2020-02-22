# Что это?

Скрипт который проверяет и начинает запись live стримов

# Как юзать?

* Поставить youtube-dl, python-twitch-client (TODO: создать requirements.txt для автоматической установки)

`pip3 install python-twitch-client youtube-dl`

* Переименовать файл conf_python.py.template в conf_python.py и добавить свой ключ (Можно получить на https://dev.twitch.tv/console)

* Переименовать файл list.sh.template в list.sh, добавить стримеров в параметре list (через пробел), изменить путь для сохранения стримов в path

* Добавить cron.sh в crontab, ну и офк убедиться что cron.service запущен (systemd timer не подойдет ибо он убивает child процессы после завершения работы родителя)
`*/5 * * * * /opt/twitch-downloader/cron.sh`

