import datetime
import os

import colorama

from utils import file_utils

colorama.init()


def get_month(n):
    return ['January',
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
            ][n - 1]


def create_message_and_save_to_log(name, string):
    file_utils.create_log_dir()

    date = datetime.date.today()

    if name:
        string = get_now_formatted() + "(" + name + ") - " + string
    else:
        string = get_now_formatted() + string

    try:
        join = os.path.join(file_utils.LOG_DIR, 'log_{}_{}.txt')
        with open(join.format(date.year, get_month(date.month)), 'a', encoding="utf-8") as file:

            file.write(string + '\n')
    except OSError:
        pass
    return str(string)


def error(text, name=''):
    print(colorama.Fore.RED, create_message_and_save_to_log(name, str(text)), sep='')


def warning(text, name=''):
    print(colorama.Fore.YELLOW, create_message_and_save_to_log(name, str(text)), sep='')


def log(text, name=''):
    print(colorama.Fore.WHITE, create_message_and_save_to_log(name, str(text)), sep='')


def debug(text, name=''):
    print(colorama.Fore.LIGHTBLACK_EX, create_message_and_save_to_log(name, str(text)), sep='')


def third_party(text, name=''):
    print('\033[92m', create_message_and_save_to_log(name, str(text)), '\033[0m', sep='')


def get_now_formatted():
    return datetime.datetime.now().strftime("[%Y-%m-%d - %H:%M:%S.%f] - ")


def format_datetime(to_format):
    return datetime.datetime.fromtimestamp(to_format)


class Logger:
    def __init__(self, debug_on, name, form="[{}] {}"):
        self.name = name
        self.form = form
        self.debug = debug_on

    def error(self, text):
        error(self.form.format(self.name, text))

    def warning(self, text):
        warning(self.form.format(self.name, text))

    def log(self, text):
        log(self.form.format(self.name, text))

    def debug(self, text):
        debug(self.form.format(self.name, text))

    def third_party(self, text):
        third_party(self.form.format(self.name, text))
