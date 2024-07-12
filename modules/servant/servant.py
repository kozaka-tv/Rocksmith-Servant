import asyncio
import logging
import os
import sys
import threading
from time import sleep

import config.log_config
from config.config_data import ConfigData
from config.config_data_helper import check_modules_enabled
from config.config_reader import ConfigReader
from modules.servant.database.db_manager import DBManager
from modules.servant.file_manager.cdlc_file_manager import FileManager
from modules.servant.scene_switcher.scene_switcher import SceneSwitcher
from modules.servant.setlist.setlist_logger import SetlistLogger
from modules.servant.song_loader.song_loader import SongLoader
from modules.servant.song_loader.songs import Songs
from utils.cmd_line_parser import parse_args
from utils.exceptions import RocksnifferConnectionError, ConfigError, RSPLNotLoggedInError, \
    RSPLPlaylistIsNotEnabledError
from utils.project_dir_setter import set_project_directory
from utils.rocksniffer import Rocksniffer

HEARTBEAT = 1
HEARTBEAT_MANAGE_SONGS = 1
HEARTBEAT_UPDATE_GAME_INFO_AND_SETLIST = 0.1

log = logging.getLogger()


class Servant:

    def __init__(self):
        log.warning("------------------------------------------------------------------------")
        log.warning("----- SERVANT IS STARTING ----------------------------------------------")
        log.warning("------------------------------------------------------------------------")

        set_project_directory()

        try:
            self.config_file_path, self.db_file_path = parse_args()
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

        config.log_config.config()

        self.conf = ConfigReader(self.config_file_path)
        try:
            config_data = ConfigData(self.conf)
        except ConfigError as e:
            log.error(e)
            sys.exit()

        # Initializing modules and utils
        self.sniffer = Rocksniffer(config_data)
        self.setlist_logger = SetlistLogger(config_data)
        self.file_manager = FileManager(config_data)
        self.songs = Songs()
        self.song_loader = SongLoader(config_data, self.songs)
        self.scene_switcher = SceneSwitcher(config_data)

        check_modules_enabled(config_data)

    def update_config(self):
        if self.conf.reload_if_changed():
            config_data_updated = ConfigData(self.conf)

            self.sniffer.update_config(config_data_updated)
            self.setlist_logger.update_config(config_data_updated)
            self.song_loader.update_config(config_data_updated)
            self.scene_switcher.update_config(config_data_updated)
            self.file_manager.update_config(config_data_updated)

            check_modules_enabled(config_data_updated)

    def get_debug_message(self):
        modules_str = "--- Enabled modules ---" + os.linesep
        if self.sniffer.enabled:
            modules_str += self.sniffer.__class__.__name__ + os.linesep
        if self.setlist_logger.enabled:
            modules_str += self.setlist_logger.__class__.__name__ + os.linesep
        if self.song_loader.enabled:
            modules_str += self.song_loader.__class__.__name__ + os.linesep
        if self.scene_switcher.enabled:
            modules_str += self.scene_switcher.__class__.__name__ + os.linesep
        if self.file_manager.enabled:
            modules_str += self.file_manager.__class__.__name__ + os.linesep

        modules_str += "---------------" + os.linesep

        sniffer_str = "Song: {sniffer.artist_name} - {sniffer.song_name} " \
                      "({sniffer.album_year}, {sniffer.album_name}), " \
                      "duration:{sniffer.song_length}s " \
                      "".format(sniffer=self.sniffer) + os.linesep

        setlist = f"Setlist: {str(self.setlist_logger.setlist)}" + os.linesep

        return os.linesep + modules_str + sniffer_str + setlist

    def in_game(self):
        return self.sniffer.enabled and self.sniffer.in_game and not self.sniffer.in_pause

    def put_the_song_into_the_setlist(self):
        if self.setlist_logger.enabled and self.in_game():
            self.setlist_logger.log_a_song(self.sniffer.artist_name + " - " + self.sniffer.song_name)

    def update_game_information(self):
        if self.sniffer.enabled:
            try:
                sniffer_not_loaded_before = self.sniffer_data_not_loaded()
                if sniffer_not_loaded_before:
                    log.warning("Trying to connect to RockSniffer to get the information from Rocksmith...")
                self.sniffer.update()
                if sniffer_not_loaded_before and self.sniffer_data_loaded():
                    log.warning("...connected to RockSniffer...sniffing")
            except RocksnifferConnectionError as rce:
                self.sniffer.memory = None
                raise rce

    def sniffer_data_loaded(self):
        return self.sniffer.memory and self.sniffer.memory is not None

    def sniffer_data_not_loaded(self):
        return not self.sniffer_data_loaded()

    def manage_songs(self, db_file):
        self.song_loader.set_db_manager(DBManager(db_file))  # because of Threading, we must set DB here

        while True:
            try:
                self.file_manager.run()
                self.song_loader.run()
                sleep(HEARTBEAT_MANAGE_SONGS)

            # Catch and log all known exceptions, but keep app alive.
            except (RSPLNotLoggedInError, RSPLPlaylistIsNotEnabledError) as ex:
                log.error(ex)

            # Catch all unchecked Exceptions, but keep app alive.
            # pylint: disable=broad-exception-caught
            except Exception as ex:
                log.exception(ex)

    def update_game_info_and_setlist(self):
        while True:
            try:
                self.update_game_information()
                self.put_the_song_into_the_setlist()
                sleep(HEARTBEAT_UPDATE_GAME_INFO_AND_SETLIST)

            # Catch all unchecked Exceptions, but keep app alive.
            # pylint: disable=broad-exception-caught
            except Exception as ex:
                log.exception(ex)

    async def run(self):

        manage_songs_thread = threading.Thread(target=self.manage_songs, args=(self.db_file_path,))
        manage_songs_thread.daemon = True
        manage_songs_thread.start()

        update_game_info_and_setlist_thread = threading.Thread(target=self.update_game_info_and_setlist)
        update_game_info_and_setlist_thread.daemon = True
        update_game_info_and_setlist_thread.start()

        while True:

            try:
                # Sleep a bit to avoid too fast processing
                await asyncio.sleep(HEARTBEAT)

                self.update_config()

            # Catch all unchecked Exceptions, but keep app alive.
            # pylint: disable=broad-exception-caught
            except Exception as e:
                log.exception(e)
