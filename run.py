import logging
import os
import sys
import threading
from time import sleep

import config.log_config
from config.config_data import ConfigData
from config.config_reader import ConfigReader
from modules.database.db_manager import DBManager
from modules.file_manager.cdlc_file_manager import FileManager
from modules.scene_switcher.scene_switcher import SceneSwitcher
from modules.setlist.setlist_logger import SetlistLogger
from modules.song_loader.song_loader import SongLoader
from modules.song_loader.songs import Songs
from utils.cmd_line_parser import parse_args
from utils.exceptions import RocksnifferConnectionError, ConfigError, RSPLNotLoggedInError, \
    RSPLPlaylistIsNotEnabledError
from utils.project_dir_setter import set_project_directory
from utils.rocksniffer import Rocksniffer

set_project_directory()

try:
    config_file_path, db_file_path = parse_args()
except ValueError as e:
    print(f"Error: {e}")
    sys.exit(1)

config.log_config.config()
log = logging.getLogger()

log.warning("------------------------------------------------------------------------")
log.warning("----- SERVANT IS STARTING ----------------------------------------------")
log.warning("------------------------------------------------------------------------")

HEARTBEAT = 1
HEARTBEAT_MANAGE_SONGS = 1
HEARTBEAT_UPDATE_GAME_INFO_AND_SETLIST = 0.1


def check_modules_enabled(config_data):
    # Search in all attributes that has "enabled" attribute
    modules_enabled = [getattr(getattr(config_data, attr), 'enabled', False) for attr in dir(config_data) if
                       not attr.startswith('__')]
    if not any(modules_enabled):
        log.error("!!! No modules are enabled !!!")


def check_enabled_module_dependencies():
    if song_loader.enabled and not file_manager.enabled:
        raise ConfigError("Please enable FileManager if you wanna use the SongLoader!")


conf = ConfigReader(config_file_path)
try:
    config_data = ConfigData(conf)
except ConfigError as e:
    log.error(e)
    sys.exit()

check_modules_enabled(config_data)

# Initializing modules and utils
sniffer = Rocksniffer(config_data)
setlist_logger = SetlistLogger(config_data)
file_manager = FileManager(config_data)
songs = Songs()
song_loader = SongLoader(config_data, songs)
scene_switcher = SceneSwitcher(config_data)
check_enabled_module_dependencies()


def update_config():
    if conf.reload_if_changed():
        config_data_updated = ConfigData(conf)

        sniffer.update_config(config_data_updated)
        setlist_logger.update_config(config_data_updated)
        song_loader.update_config(config_data_updated)
        scene_switcher.update_config(config_data_updated)
        file_manager.update_config(config_data_updated)

        check_enabled_module_dependencies()


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

    modules_str += "---------------" + os.linesep

    sniffer_str = "Song: {sniffer.artist_name} - {sniffer.song_name} " \
                  "({sniffer.album_year}, {sniffer.album_name}), " \
                  "duration:{sniffer.song_length}s " \
                  "".format(sniffer=sniffer) + os.linesep

    setlist = f"Setlist: {str(setlist_logger.setlist)}" + os.linesep

    return os.linesep + modules_str + sniffer_str + setlist


def in_game():
    return sniffer.enabled and sniffer.in_game and not sniffer.in_pause


def put_the_song_into_the_setlist():
    if setlist_logger.enabled and in_game():
        setlist_logger.log_a_song(sniffer.artist_name + " - " + sniffer.song_name)


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


def manage_songs(db_file):
    song_loader.set_db_manager(DBManager(db_file))  # because of Threading, we must set DB here

    while True:
        try:
            file_manager.run()
            song_loader.run()
            sleep(HEARTBEAT_MANAGE_SONGS)

        # Catch and log all known exceptions, but keep app alive.
        except (RSPLNotLoggedInError, RSPLPlaylistIsNotEnabledError) as ex:
            log.error(ex)

        # Catch all unchecked Exceptions, but keep app alive.
        # pylint: disable=broad-exception-caught
        except Exception as ex:
            log.exception(ex)


def update_game_info_and_setlist():
    while True:
        try:
            update_game_information()
            put_the_song_into_the_setlist()
            sleep(HEARTBEAT_UPDATE_GAME_INFO_AND_SETLIST)

        # Catch all unchecked Exceptions, but keep app alive.
        # pylint: disable=broad-exception-caught
        except Exception as ex:
            log.exception(ex)


manage_songs_thread = threading.Thread(target=manage_songs, args=(db_file_path,))
manage_songs_thread.daemon = True
manage_songs_thread.start()

update_game_info_and_setlist_thread = threading.Thread(target=update_game_info_and_setlist)
update_game_info_and_setlist_thread.daemon = True
update_game_info_and_setlist_thread.start()

while True:

    try:
        # Sleep a bit to avoid too fast processing
        sleep(HEARTBEAT)

        update_config()

    # Catch all unchecked Exceptions, but keep app alive.
    # pylint: disable=broad-exception-caught
    except Exception as e:
        log.exception(e)
