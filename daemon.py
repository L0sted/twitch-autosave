#!/usr/bin/python3

# FIXME: не создавать папки для несуществующих стримеров
# TODO: Сделать нормальную конфигурацию
# TODO: Автоматически удалять старые стримы

import os
from threading import Thread
import json
import config_python

locked_streams = list()

def which(command):
    # Пиздец, почему нет нормального аналога which из bash???
    # Мой аналог отдает true или false если есть или нет утилиты command
    for dirs in os.get_exec_path():
        if command in os.listdir(dirs):
            # Если что-нибудь нашли, то True
            return True
    # Если ничего не нашли во всех дирах, то завершает функцию с False
    return False

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
    path = config_python.path + "/"+ i
    print("Записываем стрим %s\n" % i)
    # FIXME: пофиксить абсолютный путь
    cmdline = ["youtube-dl","https://twitch.tv/"+i]
    import subprocess
    # Не хочу делать тут проверку на существование "youtube-dl" в $PATH
    s = subprocess.call(cmdline, stdout=subprocess.DEVNULL)
    print("Запись стрима %s закончена\n" % i)
    if (os.path.exists(path+"/pid")):
        os.system("rm "+path+"/pid")
        print("lock файл удален")

def checkAlive(streamers, client_id):
    '''
    1. Проверка на наличие стрима
    1.1 Если нет - удалить lock файл, если он есть
    1.2 Если есть - создать lock файл, запустить записывалку
    '''
    from twitch import TwitchClient
    client = TwitchClient(client_id=client_id)
    for i in streamers:
        # Путь до диры со стримами
        path = config_python.path + "/"+ i
        # Создаем путь до диры со стримером, если его нет
        if not (os.path.exists(config_python.path+"/"+i)):
            os.makedirs(path)
        # TODO: Сделать проверку на наличие стримера
        user_id=client.users.translate_usernames_to_ids(i)[0]['id'] # Получить ID по нику
        # Если стрим идет, то идем дальше
        if client.streams.get_stream_by_user(user_id):
            # Если стрим идет и лок файла нет, то записываем и ставим лок
            if (client.streams.get_stream_by_user(user_id).stream_type == 'live') and not (os.path.exists(config_python.path+"/"+i+"/pid")):
                print(i+" стримит")
                startRecord(i)
                os.system("touch "+path+"/pid")
            else:
                print(i+" Уже стримит")
        else:
            # Если стрим не идет, то пишем об этом и убираем его из залоченных
            print(i+" Не стримит")
            # Если есть лок, то удаляем
            if (os.path.exists(path+"/pid")):
                os.system("rm "+path+"/pid")


def removeOldStreams():
    # https://clck.ru/WHh32
    pass

if __name__ == "__main__":
    checkAlive(config_python.streamers, config_python.twitchid)
