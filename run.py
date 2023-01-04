import logging
import os
import sqlite3
from time import sleep

import config.log_config
from config.configReader import ConfigReader
from config.config_data import ConfigData
from modules.cdlc_importer.load_cdlc_json_file import CDLCImporter
from modules.file_manager.cdlc_file_manager import FileManager
from modules.scene_switcher.scene_switcher import SceneSwitcher
from modules.setlist.setlist_logger import SetlistLogger
from modules.song_loader.song_loader import SongLoader
from utils.exceptions import RocksnifferConnectionError, ConfigError
from utils.rocksniffer import Rocksniffer

HEARTBEAT = 0.1

config.log_config.config()
log = logging.getLogger()

db = sqlite3.connect('servant.db')


def check_enabled_module_dependencies():
    if song_loader.enabled and not file_manager.enabled:
        raise ConfigError("Please enable FileManager if you wanna use the SongLoader!")


log.warning("------------------------------------------------------------------------")
log.warning("----- SERVANT IS STARTING ----------------------------------------------")
log.warning("------------------------------------------------------------------------")

# OBS
# Behaviour

# Key name definitions
KEY_ENABLED = "enabled"

# Initializing configuration
conf = ConfigReader()
config_data = ConfigData(conf)

# Initializing modules and utils
sniffer = Rocksniffer(config_data)
setlist_logger = SetlistLogger(config_data)
file_manager = FileManager(config_data)
cdlc_importer = CDLCImporter(config_data, db)
song_loader = SongLoader(config_data)
scene_switcher = SceneSwitcher(config_data)
check_enabled_module_dependencies()


# TODO OBS
# TODO Behaviour


def update_config():
    if conf.reload_if_changed():
        config_data_updated = ConfigData(conf)

        sniffer.update_config(config_data_updated)
        setlist_logger.update_config(config_data_updated)
        song_loader.update_config(config_data_updated)
        scene_switcher.update_config(config_data_updated)
        file_manager.update_config(config_data_updated)
        # TODO OBS
        # TODO Behaviour

        check_enabled_module_dependencies()


# TODO move to debug Class?
def get_debug_message():
    modules_str = "--- Enabled modules ---" + os.linesep
    if sniffer.enabled:
        modules_str += sniffer.__class__.__name__ + os.linesep
    if setlist_logger.enabled:
        modules_str += setlist_logger.__class__.__name__ + os.linesep
    if song_loader.enabled:
        modules_str += song_loader.__class__.__name__ + os.linesep
    if scene_switcher.enabled:
        modules_str += scene_switcher.__class__.__name__ + os.linesep
    if file_manager.enabled:
        modules_str += file_manager.__class__.__name__ + os.linesep
    # TODO OBS
    # TODO Behaviour
    modules_str += "---------------" + os.linesep

    sniffer_str = "Song: {sniffer.artistName} - {sniffer.songName} " \
                  "({sniffer.albumYear}, {sniffer.albumName}), " \
                  "duration:{sniffer.songLength}s " \
                  "".format(sniffer=sniffer) + os.linesep

    setlist = "Setlist: {0}".format(str(setlist_logger.setlist)) + os.linesep

    return os.linesep + modules_str + sniffer_str + setlist


def in_game():
    return sniffer.enabled and sniffer.in_game and not sniffer.in_pause


def put_the_song_into_the_setlist():
    if setlist_logger.enabled and in_game():
        setlist_logger.log_a_song(sniffer.artistName + " - " + sniffer.songName)


def update_game_information():
    if sniffer.enabled:
        try:
            sniffer_not_loaded_before = sniffer_data_not_loaded()
            if sniffer_not_loaded_before:
                log.warning("Trying to connect to RockSniffer to get the information from Rocksmith...")
            sniffer.update()
            if sniffer_not_loaded_before and sniffer_data_loaded():
                log.warning("...connected to RockSniffer...sniffing")
        except RocksnifferConnectionError as rce:
            sniffer.memory = None
            raise rce


def sniffer_data_loaded():
    return sniffer.memory and sniffer.memory is not None


def sniffer_data_not_loaded():
    return not sniffer_data_loaded()


cdlc_importer.load()

# Main 'endless' loop
while True:

    try:
        # Sleep a bit to avoid too fast processing
        sleep(HEARTBEAT)

        update_config()

        scene_switcher.run()
        file_manager.run()
        song_loader.run()
        update_game_information()
        put_the_song_into_the_setlist()

    # Catch and log all the exceptions, but keep app alive.
    except Exception as e:
        log.error(e)
