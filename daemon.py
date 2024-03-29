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

log_format = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
log_file = 'output.log'
cfg_file = 'config.ini'


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


def set_config():
    """
    Эта функция либо читает существующий конфиг, либо создает новый.
    Возвращает объект конфига (configparser.ConfigParser())
    """
    config = configparser.ConfigParser()
    # Читаем конфиг, если пустой - заполняем
    if not config.read('cfg_file.ini'):
        config["app"] = {
            "path": "",
            "check_period": 5,
            "max_files": 3
        }
        config["twitch"] = {
            "app_id": "",
            "app_secret": "",
            "streamers": "t2x2,arcadia_online,252mart,the_viox"
        }
        with open('cfg_file.ini', 'w') as cfg_file:
            config.write(cfg_file)

    # Проверка конфига
    if config['twitch']['app_id'] == "" or config['twitch']['app_secret'] == "":
        log.critical("Параметры app_id или app_secret пусты. Необходимо заполнить эти параметры в конфиге. "
                     "Читай README.md")
        exit(1)

    return config


def which(command) -> bool:
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


def check_installed_tools() -> bool:
    """
    Проверяет, установлены ли необходимые утилиты
    """
    tools = ('youtube-dl', 'ffmpeg')
    for tool in tools:
        if not which(tool):
            log.critical("{} не установлен".format(tool))
            return False
    return True


def recorder(streamer):
    """
    Функция, которая запускает youtube-dl, фактически записывает стрим
    """
    streamer_path = os.path.join(config['app']['path'], streamer)
    log.info("Записываем стрим {}".format(streamer))
    # cmdline для запуска youtube-dl
    cmdline = ["youtube-dl", "-q", "-o",
               streamer_path + "/%(upload_date)s_%(title)s__%(timestamp)s_%(id)s.%(ext)s",
               "https://twitch.tv/{}".format(streamer)]
    subprocess.call(cmdline)
    log.info("Запись стрима {} закончена".format(streamer))
    if os.path.exists(os.path.join(streamer_path, "pid")):
        os.remove(os.path.join(streamer_path, "pid"))
        log.info("lock файл удален")


def get_streamer_id(streamer):
    """Получаем id стримера, при неудаче отдаем None"""
    resolved_id = twitch_client.get_users(logins=[streamer])
    if resolved_id['data']:
        return resolved_id['data'][0]['id']
    else:
        log.error(
            "Аккаунт {} не найден".format(streamer)
        )
        return None


def record_streamer(user_stream, streamer):
    """Проверяем, идет ли стрим. Если идет - записываем. Если не идет - удаляем pid файл"""
    streamer_path = os.path.join(config['app']['path'], streamer)
    if user_stream['data']:
        # Создаем путь до диры со стримером, если папка не существует
        if not (os.path.exists(streamer_path)):
            os.makedirs(streamer_path)
            log.info("Создана директория {}".format(streamer_path))

        # Если стрим идет и лок файла нет, то записываем и ставим лок
        if (user_stream['data'][0]['type'] == 'live') and not (
                os.path.exists(os.path.join(streamer_path, "pid"))):
            log.info("{} стримит".format(streamer))
            th = Thread(target=recorder, args=(streamer,))
            th.start()
            os.mknod(os.path.join(streamer_path, "pid"))
        else:
            log.info(
                "Идет запись {}".format(streamer)
            )
    else:
        # Если стрим не идет, то пишем об этом и убираем его из залоченных
        log.debug("{} не стримит".format(streamer))
        # Если есть лок, то удаляем
        if os.path.exists(os.path.join(streamer_path, "pid")):
            os.remove(os.path.join(streamer_path, "pid"))


def streamers_loop():
    """
    Цикл по стримерам
    Проходится по каждому логину, достает ID стримера,
    достает инфу о стримах, запускает функцию для записи
    """
    for streamer in config['twitch']['streamers'].split(','):

        # Достаем ID стримера, если пустой - пропускаем цикл
        user_id = get_streamer_id(streamer)
        if user_id is None:
            continue
        # Получаем данные о стриме
        user_stream = twitch_client.get_streams(user_id=user_id)
        # Запускаем запись
        record_streamer(user_stream, streamer)


def remove_old_streams():
    # https://clck.ru/WHh32
    records_path = config['app']['path']
    # По каждой папке со стримерами
    for streamer in config['twitch']['streamers']:
        try:
            streamer_dir_path = os.path.join(records_path, streamer)
            os.chdir(streamer_dir_path)
            # Если файлов в папке со стримами больше чем указано в конфиге
            if len(os.listdir(streamer_dir_path)) > int(config['app']['max_files']):
                # Получаем список файлов
                # и смотрим, превышает ли кол-во mp4 файлов заданное в конфиге
                # Если превышает - удаляем старейший
                oldest = min(os.listdir(streamer_dir_path),
                             key=os.path.getctime)
                os.unlink(oldest)
                log.warning("Удален файл: {}".format(oldest))
        except Exception as e:
            log.error(e)


if __name__ == "__main__":
    # Log config
    log = get_logger("main")

    # Проверить, установлены ли нужные утилиты
    if not check_installed_tools():
        exit()

    # Set config
    config = set_config()

    # Проверять стримы раз в check_period
    # Каждый час удалять старые стримы
    schedule.every(int(config['app']['check_period'])).seconds.do(streamers_loop)
    schedule.every(1).hours.do(remove_old_streams)

    # Инициализируем клиент твича
    twitch_client = Twitch(config['twitch']['app_id'], config['twitch']['app_secret'])
    log.info("Запущен")
    while True:
        schedule.run_pending()
        time.sleep(1)
