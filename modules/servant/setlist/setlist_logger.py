import datetime
import logging
import os
import pathlib

from utils import date_utils

LOG_SEPARATOR = "-------------------------------------------"

SETLIST_DIR = 'setlist'

log = logging.getLogger()


class SetlistLogger:

    def __init__(self, config_data):
        """
        Setlist Logger
        """
        # Init setlist directory and file
        self.enabled = config_data.setlist_logger.enabled
        if self.enabled:
            self.create_setlist_directory()
            self.file_name = setlist_file_name()
            self.write_to_setlist_file(LOG_SEPARATOR)
            self.write_to_setlist_file("Setlist of " + date_utils.now())
            self.write_to_setlist_file(LOG_SEPARATOR)

        self.setlist_path = config_data.setlist_logger.setlist_path
        self.log_file_name = "TODO.txt"
        self.setlist = []
        self.last_song = None

    def update_config(self, config_data):
        self.enabled = config_data.setlist_logger.enabled
        self.create_setlist_directory()
        self.file_name = setlist_file_name()
        self.write_to_setlist_file(LOG_SEPARATOR)
        self.write_to_setlist_file("Setlist of " + date_utils.now())
        self.write_to_setlist_file(LOG_SEPARATOR)

        self.setlist_path = config_data.setlist_logger.setlist_path
        self.log_file_name = "TODO.txt"
        self.setlist = []
        self.last_song = None

    def create_setlist_directory(self):
        if self.enabled:
            log.warning("Creating setlist directory to: %s", os.path.join(SETLIST_DIR))
            pathlib.Path(os.path.join(SETLIST_DIR)).mkdir(parents=True, exist_ok=True)

    def log_a_song(self, song):
        if song not in self.setlist:
            log.warning("Song was added to setlist: %s", song)
            self.setlist.append(song)
            self.write_to_setlist_file(song)

    def write_to_setlist_file(self, string):
        try:
            with open(self.file_name, 'a', encoding="utf-8") as file:
                file.write(string + '\n')
        except OSError:
            pass

        return str(string)


def setlist_file_name():
    date = datetime.date.today()
    join = os.path.join(SETLIST_DIR, 'setlist_{}-{}-{}.txt')
    return join.format(date.year, str(date.month).zfill(2), str(date.day).zfill(2))
