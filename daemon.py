#!/usr/bin/python3

# TODO: Перезапускать скрипт при обнаружении новой версии

import os
import sys
from threading import Thread
import configparser
import schedule
from twitchAPI.twitch import Twitch
import subprocess
import time
import logging
from logging.handlers import TimedRotatingFileHandler

log_format = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
log_file = 'output.log'
cfg_file = 'config.ini'


def set_config():
    """
    Эта функция либо читает существующий конфиг, либо создает новый.
    Возвращает объект конфига (configparser.ConfigParser())
    """
    config = configparser.ConfigParser()
    if not config.read('cfg_file.ini'):
        config["app"] = {
            "path": "",
            "check_period": 5,
            "max_files": 3
        }
        config["twitch"] = {
            "app_id": "",
            "app_secret": "",
            "streamers": "asdf,qqqqq"
        }
        with open('cfg_file.ini', 'w') as cfg_file:
            config.write(cfg_file)
    return config


def which(command):
    # Пиздец, почему нет нормального аналога which из bash???
    """
    Мой аналог which из bash'а, который отдает true или false
    при наличии или отсутствии утилиты
    """
    for dirs in os.get_exec_path():
        if command in os.listdir(dirs):
            # Если что-нибудь нашли, то True
            return True
    # Если ничего не нашли во всех дирах, то выходим с False
    return False


def check_installed_tools():
    """
    Проверяет, установлены ли необходимые утилиты
    """
    tools = ('youtube-dl', 'ffmpeg')
    for i in tools:
        if not which(i):
            log.critical(i + " не установлен")
            return False
    return True


def start_recording(i):
    """
    Функция, которая запускает в отдельном потоке запись стрима - recorder(i)
    """
    th = Thread(target=recorder, args=(i,))
    th.start()


def recorder(i):
    """
    Функция, которая запускает youtube-dl, фактически записывает стрим
    """
    path = config['app']['path'] + "/" + i
    log.info("Записываем стрим %s\n" % i)
    # cmdline для запуска youtube-dl
    cmdline = ["youtube-dl", "-q", "-o",
               path + "/%(upload_date)s_%(title)s__%(timestamp)s_%(id)s.%(ext)s",
               "https://twitch.tv/" + i]
    subprocess.call(cmdline)
    log.info("Запись стрима %s закончена\n" % i)
    if os.path.exists(path + "/pid"):
        os.remove(path + "/pid")
        log.info("lock файл удален")


def check_stream():
    # FIXME: Распилить на более мелкие функции
    """
    1. Проверка на наличие стрима
    1.1 Если нет - удалить lock файл, если он есть
    1.2 Если есть - создать lock файл, запустить записывалку
    """
    for i in config['twitch']['streamers'].split(','):
        # Путь до диры со стримами
        path = config['app']['path'] + "/" + i
        # Получаем инфо о стримере, если не получается, выходим с ошибкой

        # resolved_id = client.users.translate_usernames_to_ids(i)
        resolved_id = twitch_client.get_users(logins=[i])
        if not resolved_id['data']:
            log.error(
                "Аккаунт " + i + " не найден"
            )
            continue
        # Создаем путь до диры со стримером, если папка не существует
        if not (os.path.exists(path)):
            os.makedirs(path)
            log.info("Создана директория " + i)
        # Достаем ID стримера из инфо
        user_id = resolved_id['data'][0]['id']
        user_stream = twitch_client.get_streams(user_id=user_id)
        # Если стрим идет, то идем дальше
        if user_stream['data']:
            # Если стрим идет и лок файла нет, то записываем и ставим лок
            if (user_stream['data'][0]['type'] == 'live') and not (
                    os.path.exists(config['app']['path'] + "/" + i + "/pid")):
                log.info(i + " стримит")
                start_recording(i)
                open(config['app']['path'] + "/pid", 'w').close
            else:
                log.info(
                    "Идет запись " + i
                )
        else:
            # Если стрим не идет, то пишем об этом и убираем его из залоченных
            log.info(i + " Не стримит")
            # Если есть лок, то удаляем
            if os.path.exists(path + "/pid"):
                os.remove(path + "/pid")


def remove_old_streams():
    # https://clck.ru/WHh32
    records_path = config['app']['path']
    # По каждой папке со стримерами
    for i in config['twitch']['streamers']:
        try:
            os.chdir(records_path + "/" + i)
            # Если файлов в папке со стримами больше чем указано в конфиге
            if len(os.listdir(records_path + "/" + i)) > int(config['app']['max_files']):
                # Получаем список файлов
                # и смотрим, превышает ли кол-во mp4 файлов заданное в конфиге
                # Если превышает - удаляем старейший
                oldest = min(os.listdir(records_path + "/" + i),
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


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(logger_name):
    """
    Инициализация лога
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Console logging
    console = get_console_handler()
    console.setFormatter(CustomFormatter())
    logger.addHandler(console)

    logger.addHandler(get_file_handler())
    logger.propagate = False
    return logger


if __name__ == "__main__":
    # Проверить, установлены ли нужные утилиты
    if not check_installed_tools():
        exit()

    # Set config
    config = set_config()

    # Log config
    log = get_logger("main")
    log.info("Запущен")

    # Проверять стримы раз в check_period
    schedule.every(int(config['app']['check_period'])).seconds.do(check_stream)
    # Каждый час удалять старые стримы
    schedule.every(1).hours.do(remove_old_streams)

    twitch_client = Twitch(config['twitch']['app_id'], config['twitch']['app_secret'])
    while True:
        schedule.run_pending()
        time.sleep(1)
