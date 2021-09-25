#!/usr/bin/python3

# TODO: Перезапускать скрипт при обнаружении новой версии
# TODO: Сделать нормальную конфигурацию

import os
import sys
from threading import Thread
from types import resolve_bases
import config_python
import schedule
from twitch import TwitchClient
import subprocess
import time
import logging
from logging.handlers import TimedRotatingFileHandler
from termcolor import colored

streamers = config_python.streamers
client_id = config_python.twitchid
log_format = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
log_file = 'output.log'


def which(command):
    # Пиздец, почему нет нормального аналога which из bash???
    '''
    Мой аналог which из bash'а, который отдает true или false
    при наличии или отсутствии утилиты
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
            log.critical(i + " не установлен")
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
    path = config_python.path + "/" + i
    log.info("Записываем стрим %s\n" % i)
    # cmdline для запуска youtube-dl
    cmdline = ["youtube-dl", "-q", "-o",
               path+"/%(upload_date)s_%(title)s__%(timestamp)s_%(id)s.%(ext)s",
               "https://twitch.tv/" + i]
    subprocess.call(cmdline)
    log.info("Запись стрима %s закончена\n" % i)
    if (os.path.exists(path+"/pid")):
        os.system("rm "+path+"/pid")
        log.info("lock файл удален")


def checkAlive():
    # FIXME: Распилить ну более мелкие функции
    '''
    1. Проверка на наличие стрима
    1.1 Если нет - удалить lock файл, если он есть
    1.2 Если есть - создать lock файл, запустить записывалку
    '''
    for i in streamers:
        # Путь до диры со стримами
        path = config_python.path + "/" + i
        # Получаем инфо о стримере, если не получается, выходим с ошибкой
        resolved_id = client.users.translate_usernames_to_ids(i)
        if not resolved_id:
            log.error(
                colored(
                    "Аккаунт " + i + " не найден",
                    'red',
                )
            )
            break
        # Создаем путь до диры со стримером, если папка не существует
        if not (os.path.exists(path)):
            os.makedirs(path)
            log.info("Создана директория " + i)
        # Достаем ID стримера из инфо
        user_id = resolved_id[0]['id']
        # Если стрим идет, то идем дальше
        if client.streams.get_stream_by_user(user_id):
            # Если стрим идет и лок файла нет, то записываем и ставим лок
            if (client.streams.get_stream_by_user(user_id).stream_type == 'live') and not (os.path.exists(config_python.path+"/"+i+"/pid")):
                log.info(i + " стримит")
                startRecord(i)
                os.system("touch "+path+"/pid")
            else:
                log.info(
                    colored(
                        "Идет запись " + i,
                        'red',
                        attrs=['bold']
                    )
                )
        else:
            # Если стрим не идет, то пишем об этом и убираем его из залоченных
            log.info(i + " Не стримит")
            # Если есть лок, то удаляем
            if (os.path.exists(path+"/pid")):
                os.system("rm "+path+"/pid")


def removeOldStreams():
    # https://clck.ru/WHh32
    records_path = config_python.path
    # По каждой папке со стримерами
    for i in streamers:
        try:
            os.chdir(records_path+"/"+i)
            # Если файлов в папке со стримами больше чем указано в конфиге
            if len(os.listdir(records_path+"/"+i)) > config_python.max_files:
                # Получаем список файлов
                # и смотрим, превышает ли кол-во mp4 файлов заданное в конфиге
                # Если превышает - удаляем старейший
                oldest = min(os.listdir(records_path+"/"+i),
                             key=os.path.getctime)
                os.unlink(oldest)
                log.warning("Удален файл: " + oldest)
        except Exception as e:
            log.error(e)


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(log_file, when='midnight')
    file_handler.setFormatter(log_format)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    logger.propagate = False
    return logger


if __name__ == "__main__":
    # Проверить, установлены ли нужные утилиты
    if not checkTools():
        exit()

    # Log config
    log = get_logger("main")
    log.info("Запущен")

    # Проверять стримы раз в check_period
    schedule.every(config_python.check_period).seconds.do(checkAlive)
    # Каждый час удалять старые стримы
    schedule.every(1).hours.do(removeOldStreams)

    client = TwitchClient(client_id=client_id)
    while True:
        schedule.run_pending()
        time.sleep(1)
