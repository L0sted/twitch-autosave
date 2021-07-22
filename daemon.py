#!/usr/bin/python3

# TODO: Сделать проверку на наличие стримера
# FIXME: не создавать папки для несуществующих стримеров
# TODO: Сделать нормальную конфигурацию
# TODO: Автоматически удалять старые стримы
# TODO: сделать возможность добавлять свои параметры в cmdline к команде записи

import os
from threading import Thread
import config_python
import schedule
from twitch import TwitchClient
import subprocess
import time
streamers = config_python.streamers
client_id = config_python.twitchid


def which(command):
    # Пиздец, почему нет нормального аналога which из bash???
    '''
    Мой аналог which из bash'а, который отдает true или false при наличии или отсутствии утилиты    
    '''
    for dirs in os.get_exec_path():
        if command in os.listdir(dirs):
            # Если что-нибудь нашли, то True
            return True
    # Если ничего не нашли во всех дирах, то выходим с False
    return False

def checkTools():
    '''
    Проверяет, установлены ли необходимые утилиты
    '''
    tools = ('youtube-dl', 'ffmpeg')
    for i in tools:
        if not which(i):
            print(i + " не установлен")
            return False
    return True

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
    # cmdline для запуска youtube-dl 
    cmdline = ["youtube-dl","https://twitch.tv/"+i]
    s = subprocess.call(cmdline, stdout=subprocess.DEVNULL)
    print("Запись стрима %s закончена\n" % i)
    if (os.path.exists(path+"/pid")):
        os.system("rm "+path+"/pid")
        print("lock файл удален")

def checkAlive():
    '''
    1. Проверка на наличие стрима
    1.1 Если нет - удалить lock файл, если он есть
    1.2 Если есть - создать lock файл, запустить записывалку
    '''
    client = TwitchClient(client_id=client_id)
    for i in streamers:
        # Путь до диры со стримами
        path = config_python.path + "/"+ i
        # Создаем путь до диры со стримером, если его нет
        if not (os.path.exists(path)):
            os.makedirs(path)
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
    if not checkTools(): exit()
    schedule.every(config_python.period).minutes.do(checkAlive)
    while True:
        schedule.run_pending()
        time.sleep(1)    
