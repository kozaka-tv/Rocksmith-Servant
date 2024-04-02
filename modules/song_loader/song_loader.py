import fnmatch
import logging
import os
from time import time

from config.config_data import ConfigData
from definitions import PSARC_INFO_FILE_CACHE_DIR, CDLC_INFO_FILE_EXT, CDLC_FILE_EXT, EXTENSION_PSARC_INFO_JSON
from modules.database.db_manager import DBManager
from modules.song_loader.song_data import SongData
from modules.song_loader.song_loader_utils import playlist_does_not_changed, update_tags, \
    check_cdlc_archive_dir, check_rocksmith_cdlc_dir
from utils import file_utils, rs_playlist, psarc_reader
from utils.exceptions import BadDirectoryError
from utils.exceptions import RSPlaylistNotLoggedInError
from utils.rs_playlist import get_playlist, is_user_not_logged_in

DEFAULT_CDLC_DIR = 'import'
HEARTBEAT = 5

log = logging.getLogger()
LOG_DEBUG_IS_ENABLED = log.isEnabledFor(logging.DEBUG)


class SongLoader:
    def __init__(self, config_data: ConfigData, db_manager: DBManager, songs):
        self.enabled = config_data.song_loader.enabled
        if self.enabled:
            self.twitch_channel = config_data.song_loader.twitch_channel
            self.phpsessid = config_data.song_loader.phpsessid
            self.rsplaylist = None
            self.rsplaylist_updated = True
            self.cdlc_dir = os.path.join(config_data.song_loader.cdlc_dir)
            self.rspl_tags = config_data.song_loader.rspl_tags
            self.cfsm_file_name = config_data.song_loader.cfsm_file_name
            self.cdlc_archive_dir = check_cdlc_archive_dir(config_data.song_loader.cdlc_archive_dir)
            self.destination_directory = config_data.song_loader.destination_directory
            self.rocksmith_cdlc_dir = check_rocksmith_cdlc_dir(config_data.song_loader.rocksmith_cdlc_dir)
            self.allow_load_when_in_game = config_data.song_loader.allow_load_when_in_game
            self.cdlc_import_json_file = config_data.song_loader.cdlc_import_json_file
            self.songs_to_load = os.path.join(config_data.song_loader.cdlc_dir, config_data.song_loader.cfsm_file_name)

            try:
                self.create_directories()
            except FileNotFoundError as bde:
                log.error("---------------------------------------")
                log.error("Directory %s could not be created!", bde.filename)
                log.error("Please fix the configuration!")
                log.error("---------------------------------------")
                raise BadDirectoryError

            # TODO really it is needed to store and have as input the DBManger + db? Is import not enough?
            self.db_manager = db_manager
            self.db = db_manager.db
            self.songs = songs

            # TODO commented out for work
            # TODO commented out for work
            # TODO commented out for work
            # TODO commented out for work
            self.update_all_cdlc_file_information()
            self.__get_psarc_information_for_new_files_in_dir(self.cdlc_archive_dir)

            self.last_run = time()

    def update_config(self, config_data):
        self.enabled = config_data.song_loader.enabled
        self.cdlc_dir = os.path.join(config_data.song_loader.cdlc_dir)
        self.rspl_tags = config_data.song_loader.rspl_tags
        self.cfsm_file_name = config_data.song_loader.cfsm_file_name
        self.cdlc_archive_dir = check_cdlc_archive_dir(config_data.song_loader.cdlc_archive_dir)
        self.destination_directory = config_data.song_loader.destination_directory
        self.rocksmith_cdlc_dir = check_rocksmith_cdlc_dir(config_data.song_loader.rocksmith_cdlc_dir)
        self.allow_load_when_in_game = config_data.song_loader.allow_load_when_in_game
        self.phpsessid = config_data.song_loader.phpsessid
        self.cdlc_import_json_file = config_data.song_loader.cdlc_import_json_file
        self.songs_to_load = os.path.join(config_data.song_loader.cdlc_dir, config_data.song_loader.cfsm_file_name)

        self.create_directories()

    def create_directories(self):
        file_utils.create_directory_logged(PSARC_INFO_FILE_CACHE_DIR)
        file_utils.create_directory_logged(self.cdlc_dir)
        file_utils.create_directory_logged(self.cdlc_archive_dir)
        file_utils.create_directory_logged(self.rocksmith_cdlc_dir)

    def run(self):
        if self.enabled:
            if time() - self.last_run >= HEARTBEAT:
                # log.info("Load songs according to the requests!")

                if self.update_playlist():
                    log.info("Playlist has been changed, update songs!")
                    self.update_cdlc_files_in_rs_dir()

                    # TODO or maybe this should be configurable?
                    # else:  # load songs only in case we are not in game to avoid lagging in game

                    self.move_requested_cdlc_files_to_destination()
                else:
                    # TODO Maybe, this is not completely true! If the file is not parsed, then it will be not checked.
                    #   I think, the logic must be separated.
                    #   1) rs playlist NOT updated --> Just check dirs and move files
                    #   2) rs playlist UPDATED --> check DB and move files
                    log.info("No rsplaylist change, nothing to do...")

                self.last_run = time()

    def update_playlist(self):
        new_playlist = get_playlist(self.twitch_channel, self.phpsessid)

        self.exit_if_user_is_not_logged_in_on_rspl_page(new_playlist)

        if self.rsplaylist is None:
            self.rsplaylist = new_playlist
            log.info("Initial load of the rsplaylist done...")
            return True

        if playlist_does_not_changed(self.rsplaylist, new_playlist):
            return False

        log.info("Playlist has been changed, lets update!")

        self.rsplaylist = new_playlist

        return True

    def exit_if_user_is_not_logged_in_on_rspl_page(self, new_playlist):
        for sr in new_playlist["playlist"]:
            for cdlc in sr["dlc_set"]:
                if is_user_not_logged_in(cdlc):
                    self.rsplaylist = None
                    self.last_run = time()
                    log.error("User must be logged in into RS playlist to be able to use the module!")
                    raise RSPlaylistNotLoggedInError
                else:
                    return

    def update_all_cdlc_file_information(self):
        filenames_from_cache_dir = self.__get_cdlc_filenames_from_cache_dir()
        filenames_from_archive_dir = self.__get_cdlc_filenames_from_archive_dir()
        filenames_from_rs_dir = self.__get_cdlc_filenames_from_rs_dir()

        self.__clean_up_archive_dir_for_duplicates(filenames_from_rs_dir, filenames_from_archive_dir)

        self.__get_psarc_information_for_new_files_in_dir(self.rocksmith_cdlc_dir, filenames_from_cache_dir)
        self.__get_psarc_information_for_new_files_in_dir(self.cdlc_archive_dir, filenames_from_cache_dir)

        # TODO not needed!
        # TODO not needed!
        # TODO not needed!
        # TODO not needed!
        # TODO not needed!
        # TODO not needed!
        # TODO not needed!
        # TODO not needed!
        # self.__update_cdlc_files_in_archive_dir(filenames_from_archive_dir)

        # ---------- TODO cleanup cache --> Or clean up only at start?
        log.info('Count of files in cache: %s', len(filenames_from_cache_dir))
        log.info('Count of files in archive: %s', len(filenames_from_archive_dir))
        log.info('Count of files in rs: %s', len(filenames_from_rs_dir))
        # TODO files_in_rs
        # TODO files_in_cache
        # TODO cleanup cache

    @staticmethod
    def __get_cdlc_filenames_from_cache_dir():
        return file_utils.get_file_names_from(PSARC_INFO_FILE_CACHE_DIR, CDLC_INFO_FILE_EXT)

    def __get_cdlc_filenames_from_archive_dir(self):
        return file_utils.get_file_names_from(self.cdlc_archive_dir)

    def __get_cdlc_filenames_from_rs_dir(self):
        return file_utils.get_file_names_from(self.rocksmith_cdlc_dir)

    def __clean_up_archive_dir_for_duplicates(self, filenames_from_rs_dir, filenames_from_archive_dir):
        files_to_clean_up = set(filenames_from_rs_dir).intersection(filenames_from_archive_dir)

        if len(files_to_clean_up) > 0:
            log.warning(
                "Duplicated CDLC files found in the archive and under RS! Files to be deleted from the archive: %s",
                files_to_clean_up)

        for filename in files_to_clean_up:
            file_utils.delete_file(self.cdlc_archive_dir, filename)

    def __get_psarc_information_for_new_files_in_dir(self, directory, filenames_from_cache_dir):
        log.info('Reading and updating cache files from directory: %s', directory)

        # if LOG_DEBUG_IS_ENABLED:
        #     log.debug("----- Files ------------------------------------------")

        counter = 0
        cdlc_files = set()  # TODO needed this set?
        for root, dir_names, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, CDLC_FILE_EXT):
                try:
                    filenames_from_cache_dir.remove(filename + EXTENSION_PSARC_INFO_JSON)
                except KeyError:
                    song_data = self.__extract_song_information(directory, filename)
                    cdlc_files.add(filename)
                    counter += 1
                    # if LOG_DEBUG_IS_ENABLED:
                    # TODO correct log level
                    log.warning("Extracted information for the file: %s", filename)

        log.info("---------- Extracted %s cdlc information", counter)
        if LOG_DEBUG_IS_ENABLED:
            log.debug("Extracted information for the file: %s", cdlc_files)

        # TODO no need to return anything!
        return cdlc_files

    def __update_cdlc_files_in_archive_dir(self, cdlc_file_names):
        counter = 0
        for cdlc_file_name in cdlc_file_names:
            # TODO inline
            song_data = self.extract_song_information_from_archive_dir(cdlc_file_name)
            self.songs.archive.add(song_data)
            counter += 1
            if counter % 500 == 0:
                log.info(f"Extracted {counter} CDLCs")

            # if len(self.songs.missing_from_archive) > 0:
            #     self.songs.missing_from_archive.discard(cdlc_file_name)

        log.info('Song data for the %s into Rocksmith loaded CDLC files were extracted.', len(cdlc_file_names))

        return cdlc_file_names

    def update_cdlc_files_in_rs_dir(self):
        cdlc_files = self.__get_cdlc_filenames_from_rs_dir()

        for cdlc_file_name in cdlc_files:
            self.songs.loaded_into_rs.add(cdlc_file_name)

            # TODO temporary commented out because this is a draft!
            # TODO temporary commented out because this is a draft!
            # TODO temporary commented out because this is a draft!
            # TODO temporary commented out because this is a draft!
            song_data = self.extract_song_information_from_rs_dir(cdlc_file_name)
            self.songs.loaded_into_rs_with_song_data.add(song_data)

            if len(self.songs.missing_from_archive) > 0:
                self.songs.missing_from_archive.discard(cdlc_file_name)

        log.info('Song data for the %s into Rocksmith loaded CDLC files were extracted.', len(cdlc_files))

    def extract_song_information_from_rs_dir(self, cdlc_file_name: str):
        return self.__extract_song_information(self.rocksmith_cdlc_dir, cdlc_file_name)

    def extract_song_information_from_archive_dir(self, cdlc_file_name: str):
        return self.__extract_song_information(self.cdlc_archive_dir, cdlc_file_name)

    @staticmethod
    def __extract_song_information(directory, cdlc_file_name: str):
        song_data = SongData()
        # TODO set cdlc_file_name into song_data here, or earlier? Or even later?
        song_data.song_file_name = cdlc_file_name
        file_path_to_extract = os.path.join(directory, cdlc_file_name)
        # TODO write_to_file is True here, to keep the json in the cache. Is this not always True?
        psarc_reader.extract_psarc(file_path_to_extract, song_data, True)
        return song_data

    # TODO refactor this. it should be like
    # - get_requests from RS playlist
    # - get filenames from DB
    # - move files
    def move_requested_cdlc_files_to_destination(self):
        for sr in self.rsplaylist["playlist"]:
            rspl_request_id = sr['id']
            for dlc_set in sr["dlc_set"]:
                rspl_song_id = dlc_set['id']
                cdlc_id = dlc_set["cdlc_id"]
                artist = dlc_set["artist"]
                title = dlc_set["title"]

                # TODO if it is possible, do not create always a new SongData. If it is already exists, just reuse it!
                #      search in a list
                song_data = SongData(rspl_request_id, cdlc_id, rspl_song_id, artist, title)
                song_data.rspl_official = dlc_set["official"]
                song_data.rspl_position = str(sr["position"])
                log.debug("Request: %s", song_data)

                update_tags(song_data, sr)

                # Do not load official DLC files
                if song_data.is_official:  # TODO #113 some ODLC-s were here not skipped! Maybe different official id?
                    log.debug("Skipping ODLC: %s", song_data)
                    continue

                rows = self.db_manager.search_song_in_the_db(artist, title)

                if len(rows) > 0:
                    log.debug("---- sr %s -------", song_data.rspl_position)
                    for element in rows:
                        song_file_name = str(element[0])
                        song_data.song_file_name = song_file_name

                        log.debug("row=%s", song_file_name)
                        self.songs.songs_from_archive_need_to_be_loaded.add(song_data)
                else:
                    log.debug("User must download the song: cdlc_id=%s - %s - %s", cdlc_id, artist, title)
                    # rs_playlist.set_tag_to_download(self.twitch_channel,
                    #                                 self.phpsessid,
                    #                                 song_data.rspl_request_id,
                    #                                 self.rspl_tags)

        if len(self.songs.songs_from_archive_need_to_be_loaded) <= 0:
            log.info("---- No new file must be moved and loaded from archive!")
            return

        log.info("---- Files to move from archive according to the requests: %s",
                 str(self.songs.songs_from_archive_need_to_be_loaded))

        actually_loaded_songs = set()
        for song_data in self.songs.songs_from_archive_need_to_be_loaded:
            if song_data.song_file_name in self.songs.loaded_into_rs:

                if self.rspl_tags.tag_loaded not in song_data.tags:
                    self.set_tag_loaded(song_data)
            else:
                song_to_move = os.path.join(self.cdlc_archive_dir, song_data.song_file_name)
                moved = file_utils.move_file(song_to_move, self.destination_directory)
                if moved:
                    log.debug("The song were moved from the archive to under RS. Moved file: %s", song_to_move)
                    self.songs.loaded_into_rs.add(song_data.song_file_name)
                    actually_loaded_songs.add(song_data.song_file_name)
                    # TODO this takes 1 sec for each call. If we have a list of 30 songs, it could take 30 seconds!
                    #   Do it only once!
                    rs_playlist.set_tag_loaded(self.twitch_channel,
                                               self.phpsessid,
                                               song_data.rspl_request_id,
                                               self.rspl_tags)
                else:
                    log.debug("Could not move file: %s", song_to_move)
                    self.songs.missing_from_archive.add(song_data.song_file_name)
                    song_data.missing = True
                    # TODO this takes 1 sec for each call. If we have a list of 30 songs, it could take 30 seconds!
                    #   Do it only once!
                    rs_playlist.set_tag_to_download(self.twitch_channel, self.phpsessid, song_data.rspl_request_id,
                                                    self.rspl_tags)

        if len(actually_loaded_songs) > 0:
            log.warning("---- Files newly moved and will be parsed: %s", str(actually_loaded_songs))
        if len(self.songs.missing_from_archive) > 0:
            log.error("---- Missing files but found in Database: %s", str(self.songs.missing_from_archive))

    def set_tag_loaded(self, song_data):
        rs_playlist.set_tag_loaded(self.twitch_channel,
                                   self.phpsessid,
                                   song_data.rspl_request_id,
                                   self.rspl_tags)
        song_data.tags.add(self.rspl_tags.tag_loaded)
        # song_data.tags.discard('need to download')  # TODO
