#!/usr/bin/python3

# база со стримерами в json файле

from threading import Thread
import json
import config_python


def startRecord(i):
    '''
    Функция, которая запускает в отдельном потоке запись стрима - recorder(i)
    '''
    th = Thread(target=recorder, args=(i, ))
    th.start()

def recorder(i):
    '''
    Функция, которая запускает youtube-dl, фактически записывает стрим
    '''
    print("Записываем стрим %s\n" % i)
    # FIXME: пофиксить абсолютный путь
    cmdline = ["/home/losted/.local/bin/youtube-dl","twitch.tv/"+i]
    import subprocess
    s = subprocess.call(cmdline)
    print("Запись стрима %s закончена\n" % i)

def checkAlive(streamers, client_id):
    '''
    1. Проверка на наличие стрима
    1.1 Если нет - удалить lock файл, если он есть
    1.2 Если есть - создать lock файл, запустить записывалку
    '''

    from twitch import TwitchClient
    client = TwitchClient(client_id=client_id)

    for i in streamers:
        # Если есть такой стример - проверяем, идет ли стрим
        user_id=client.users.translate_usernames_to_ids(i)[0]['id'] #Получить ID по нику
        # Это зачем проверка?
        if client.streams.get_stream_by_user(user_id):
            # Если стрим идет то записываем
            if client.streams.get_stream_by_user(user_id).stream_type == 'live':
                startRecord(i)
        else:
            print(i+" Не стримит")



if __name__ == "__main__":
    checkAlive(config_python.streamers, config_python.twitchid)
