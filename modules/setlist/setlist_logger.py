import datetime
import logging
import os
import pathlib

LOG_SEPARATOR = "-------------------------------------------"

SETLIST_DIR = 'setlist'

log = logging.getLogger()


class SetlistLogger:
    # TODO add params like file location
    def __init__(self, config_data):
        """
        Setlist Logger
        """
        # Init setlist directory and file
        self.enabled = config_data.setlist_logger.enabled
        if self.enabled:
            # TODO this should be maybe in run?
            self.create_setlist_directory()
            self.file_name = setlist_file_name()
            self.write_to_setlist_file(LOG_SEPARATOR)
            self.write_to_setlist_file("Setlist of " + str(datetime.datetime.now()))
            self.write_to_setlist_file(LOG_SEPARATOR)

        self.setlist_path = config_data.setlist_logger.setlist_path
        # TODO
        self.log_file_name = "TODO.txt"
        self.setlist = []
        self.last_song = None

    def update_config(self, config_data):
        # TODO use enabled, and do nothing if disabled
        self.enabled = config_data.setlist_logger.enabled
        self.create_setlist_directory()
        self.file_name = setlist_file_name()
        self.write_to_setlist_file(LOG_SEPARATOR)
        self.write_to_setlist_file("Setlist of " + str(datetime.datetime.now()))
        self.write_to_setlist_file(LOG_SEPARATOR)

        self.setlist_path = config_data.setlist_logger.setlist_path
        # TODO
        self.log_file_name = "TODO.txt"
        self.setlist = []
        self.last_song = None

    def create_setlist_directory(self):
        if self.enabled:
            log.warning("Creating setlist directory to: {}".format(os.path.join(SETLIST_DIR)))
            pathlib.Path(os.path.join(SETLIST_DIR)).mkdir(parents=True, exist_ok=True)

    def log_a_song(self, song):
        if song not in self.setlist:
            log.info("Song was added to setlist: " + song)
            self.setlist.append(song)
            self.write_to_setlist_file(song)

    def write_to_setlist_file(self, string):
        try:
            # TODO maybe we should save the file to this Class and then just append. What if crash or exit?
            with open(self.file_name, 'a', encoding="utf-8") as file:
                file.write(string + '\n')
        except OSError as exc:
            pass
        return str(string)


def setlist_file_name():
    date = datetime.date.today()
    join = os.path.join(SETLIST_DIR, 'setlist_{}-{}-{}.txt')
    return join.format(date.year, str(date.month).zfill(2), str(date.day).zfill(2))
