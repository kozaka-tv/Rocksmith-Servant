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
        string = get_date() + "(" + name + ") - " + string
    else:
        string = get_date() + string

    try:
        join = os.path.join(file_utils.LOG_DIR, 'log_{}_{}.txt')
        with open(join.format(date.year, get_month(date.month)), 'a', encoding="utf-8") as file:

            file.write(string + '\n')
    except OSError:
        pass
    return str(string)


def warning(text, name=''):
    print(colorama.Fore.RED, create_message_and_save_to_log(name, str(text)), sep='')


def notice(text, name=''):
    print(colorama.Fore.YELLOW, create_message_and_save_to_log(name, str(text)), sep='')


def log(text, name=''):
    print(colorama.Fore.CYAN, create_message_and_save_to_log(name, str(text)), sep='')


def discrete(text, name=''):
    print(colorama.Fore.LIGHTBLACK_EX, create_message_and_save_to_log(name, str(text)), sep='')


def third_party(text, name=''):
    print('\033[92m', create_message_and_save_to_log(name, str(text)), '\033[0m', sep='')


def get_date():
    return datetime.datetime.now().strftime("[%Y-%m-%d - %H:%M:%S.%f] - ")


class Logger:
    def __init__(self, name, form="[{}] {}"):
        self.name = name
        self.form = form

    def warning(self, text):
        warning(self.form.format(self.name, text))

    def notice(self, text):
        notice(self.form.format(self.name, text))

    def log(self, text):
        log(self.form.format(self.name, text))

    def discrete(self, text):
        discrete(self.form.format(self.name, text))

    def third_party(self, text):
        third_party(self.form.format(self.name, text))
