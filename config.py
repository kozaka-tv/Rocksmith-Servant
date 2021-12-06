import log

from iniReader import INIReader

global conf


def load_config_ini(self):
    self.conf = None
    try:
        self.conf = INIReader("config.ini")
    except FileNotFoundError:
        log.notice('A config.ini file was created. Fill it, then relaunch RocksmithSceneSwitcher.')
        log.notice('Press any key to exit this program.')
        input()
        exit(0)
