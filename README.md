# Что это?

Скрипт, который записывает стримы с твича, удаляет старые, ведет красивый лог с цветами (Alpha)

# Как юзать?

* Поставить youtube-dl, ffmpeg и другие пакеты из requirements.txt

`apt install youtube-dl ffmpeg -y`

`pip install -r requirements.txt`

* Создать файл conf_python.py и добавить свой ключ (Можно получить на https://dev.twitch.tv/console), а также переменные из config_python.py.template: 

```
twitchid = "ID" # ID ключа
streamers = ("jesusavgn", "252mart", "vi0xxx") # список стримеров в таком формате
path = "/путь/до/диры/со/стримами" # путь до директории, куда писать стримы
check_period = 5 # Частота проверки стримеров (в секундах)
max_files = 3 # Сколько хранить стримов
```

* Запустить скрипт в screen'е или создать для него systemd.service файл (или init.d, в зависимости от системы инициализации)