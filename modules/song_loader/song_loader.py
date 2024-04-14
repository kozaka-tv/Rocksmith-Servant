import logging
import os
from time import time

from config.config_data import ConfigData
from definitions import PSARC_INFO_FILE_CACHE_DIR, EXT_PSARC_INFO_JSON, PATTERN_CDLC_INFO_FILE_EXT
from modules.database.db_manager import DBManager
from modules.song_loader.song_data import SongData
from modules.song_loader.song_loader_helper import playlist_does_not_changed, check_cdlc_archive_dir, \
    check_rocksmith_cdlc_dir, update_tags_in_song_data, is_official
from utils import file_utils, rs_playlist, psarc_reader
from utils.collection_utils import is_not_empty, is_empty, repr_in_multi_line
from utils.exceptions import BadDirectoryError
from utils.exceptions import RSPLNotLoggedInError
from utils.rs_playlist import get_playlist, user_is_not_logged_in

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

            self.__create_directories()

            # TODO really it is needed to store and have as input the DBManger + db? Is import not enough?
            self.db_manager = db_manager
            self.db = db_manager.db
            self.songs = songs

            self.__init_and_cleanup_songs_data()

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

        self.__create_directories()

    def __create_directories(self):
        try:
            file_utils.create_directory_logged(PSARC_INFO_FILE_CACHE_DIR)
            file_utils.create_directory_logged(self.cdlc_dir)
            file_utils.create_directory_logged(self.cdlc_archive_dir)
            file_utils.create_directory_logged(self.rocksmith_cdlc_dir)
        except FileNotFoundError as bde:
            log.error("---------------------------------------")
            log.error("Directory %s could not be created!", bde.filename)
            log.error("Please fix the configuration!")
            log.error("---------------------------------------")
            raise BadDirectoryError

    def run(self):
        if self.enabled:
            if time() - self.last_run >= HEARTBEAT:

                if self.playlist_has_been_changed():
                    log.info("Playlist has been changed, update songs!")

                    self.__find_existing_song_filenames_from_db_according_to_the_requests()

                    # TODO do update of DB and lists?

                    self.__calculate_songs_need_to_be_moved_from_archive_to_under_rs()

                    # TODO or maybe this should be configurable?
                    # else:  # load songs only in case we are not in game to avoid lagging in game

                    self.__move_requested_cdlc_files_from_archive_to_rs()

                else:
                    # TODO Maybe, this is not completely true! If the file is not parsed, then it will be not checked.
                    #   I think, the logic must be separated.
                    #   1) rs playlist NOT updated --> Just check dirs and move files
                    #   2) rs playlist UPDATED --> check DB and move files
                    log.info("No rsplaylist change, nothing to do...")

                self.last_run = time()

    def playlist_has_been_changed(self):
        new_playlist = get_playlist(self.twitch_channel, self.phpsessid)

        self.__stop_if_user_is_not_logged_in_on_rspl_page(new_playlist)

        if self.rsplaylist is None:
            self.rsplaylist = new_playlist
            log.info("Initial load of the playlist is done...")
            return True

        if playlist_does_not_changed(self.rsplaylist, new_playlist):
            return False

        log.info("Playlist has been changed, lets update!")

        self.rsplaylist = new_playlist

        return True

    def __stop_if_user_is_not_logged_in_on_rspl_page(self, new_playlist):
        not_logged_in = user_is_not_logged_in(new_playlist)

        if not_logged_in is None:
            log.debug("Playlist is empty! Can not tell, that the user is logged in or not!")

        elif not_logged_in:
            self.rsplaylist = None
            self.last_run = time()
            log.error("User is not logged in! Please log in on RSPL!")
            raise RSPLNotLoggedInError

        else:
            log.debug("User is logged in and there is at least one request on the list.")

    def __init_and_cleanup_songs_data(self):
        log.warning('Initialising and cleaning up all CDLC file information')

        filenames_from_cache_dir = self.__get_cdlc_filenames_from_cache_dir()
        filenames_from_archive_dir = self.__get_cdlc_filenames_from_archive_dir()
        filenames_from_rs_dir = self.__get_cdlc_filenames_from_rs_dir()

        self.__clean_up_archive_dir_for_duplicates(filenames_from_rs_dir, filenames_from_archive_dir)

        filenames_in_rs_and_archive_dir = filenames_from_rs_dir.union(filenames_from_archive_dir)
        filenames_in_db = self.db_manager.all_song_filenames()
        self.__clean_up_songs_in_db(filenames_in_rs_and_archive_dir, filenames_in_db)
        self.__clean_up_songs_in_cache(filenames_in_rs_and_archive_dir, filenames_from_cache_dir)

        self.__store_songs_in_db(self.rocksmith_cdlc_dir, filenames_from_rs_dir)
        self.__store_songs_in_db(self.cdlc_archive_dir, filenames_from_archive_dir)

        # TODO store lists in memory (songs)?

        # ---------- TODO cleanup cache --> Or clean up only at start? --> Or lower log level
        log.info('Count of files in cache: %s', len(filenames_from_cache_dir))
        log.info('Count of files in archive: %s', len(filenames_from_archive_dir))
        log.info('Count of files in rs: %s', len(filenames_from_rs_dir))
        # TODO files_in_rs
        # TODO files_in_cache
        # TODO cleanup cache

    @staticmethod
    def __get_cdlc_filenames_from_cache_dir():
        return file_utils.get_file_names_from(PSARC_INFO_FILE_CACHE_DIR, PATTERN_CDLC_INFO_FILE_EXT)

    def __get_cdlc_filenames_from_archive_dir(self):
        return file_utils.get_file_names_from(self.cdlc_archive_dir)

    def __get_cdlc_filenames_from_rs_dir(self):
        return file_utils.get_file_names_from(self.rocksmith_cdlc_dir)

    def __clean_up_archive_dir_for_duplicates(self, filenames_from_rs_dir, filenames_from_archive_dir):
        log.info('Cleaning up archive dir for duplicates')
        duplicates = set(filenames_from_rs_dir).intersection(filenames_from_archive_dir)
        if is_not_empty(duplicates):
            self.__remove_duplicates(duplicates, filenames_from_archive_dir)

    # TODO move into the helper!?
    def __clean_up_songs_in_db(self, filenames_in_rs_and_archive_dir, filenames_in_db):
        log.info('Cleaning up songs in DB')
        to_delete = filenames_in_db.difference(filenames_in_rs_and_archive_dir)
        if is_not_empty(to_delete):
            log.info("Count of songs to be deleted: %s", len(to_delete))
            self.db_manager.delete_song_by_filename(to_delete)

            for filename_to_delete in to_delete:
                log.debug("Song has been deleted: %s", filename_to_delete)
                filenames_in_db.discard(filename_to_delete)

    # TODO move into the helper!?
    def __clean_up_songs_in_cache(self, filenames_in_rs_and_archive_dir, filenames_from_cache_dir):
        log.info('Cleaning up songs in cache')
        to_delete = filenames_from_cache_dir.difference(filenames_in_rs_and_archive_dir)
        if is_not_empty(to_delete):
            log.info("Count of songs to be deleted: %s", len(to_delete))
            for filename_to_delete in to_delete:
                filename_complete = filename_to_delete + EXT_PSARC_INFO_JSON
                log.debug("Song info file has been deleted: %s", filename_complete)
                file_utils.delete_file(PSARC_INFO_FILE_CACHE_DIR, filename_complete)
                filenames_from_cache_dir.remove(filename_to_delete)
                pass

    def __remove_duplicates(self, duplicates, filenames_from_archive_dir):
        log.warning("Duplicated CDLC files found in the archive and under RS! Files to be deleted from the archive: %s",
                    duplicates)
        for filename in duplicates:
            file_utils.delete_file(self.cdlc_archive_dir, filename)
            filenames_from_archive_dir.remove(filename)

    def __store_songs_in_db(self, directory, filenames):
        log.info('Reading new psarc files from directory: %s', directory)

        counter = 0
        # cdlc_files = set()  # TODO needed this set? --> In case we want all data in memory? Then yes.

        for filename in filenames:
            if not self.db_manager.is_song_by_filename_exists(filename):

                song_data = self.__extract_song_information(directory, filename)
                self.db_manager.insert_song(song_data)
                # cdlc_files.add(song_data)
                counter += 1
                if counter % 100 == 0:
                    log.info(f"Extracted and inserted {counter} CDLCs into the DB")

        log.info("---------- Stored %s new song(s) in DB", counter)

        # TODO needed this return
        # return cdlc_files

    # TODO not used!
    # def __update_cdlc_files_in_archive_dir(self, cdlc_file_names):
    #     counter = 0
    #     for cdlc_file_name in cdlc_file_names:
    #         # TODO inline
    #         song_data = self.__extract_song_information_from_archive_dir(cdlc_file_name)
    #         self.songs.archive.add(song_data)
    #         counter += 1
    #         if counter % 500 == 0:
    #             log.info(f"Extracted {counter} CDLCs")
    #
    #         # if len(self.songs.missing_from_archive) > 0:
    #         #     self.songs.missing_from_archive.discard(cdlc_file_name)
    #
    #     log.info('Song data for the %s into Rocksmith loaded CDLC files were extracted.', len(cdlc_file_names))
    #
    #     return cdlc_file_names

    # TODO not used!
    # def update_cdlc_files_in_rs_dir(self):
    #     cdlc_files = self.__get_cdlc_filenames_from_rs_dir()
    #
    #     for cdlc_file_name in cdlc_files:
    #         self.songs.loaded_into_rs.add(cdlc_file_name)
    #
    #         TODO temporary commented out because this is a draft!
    #         TODO temporary commented out because this is a draft!
    #         TODO temporary commented out because this is a draft!
    #         TODO temporary commented out because this is a draft!
    #         song_data = self.__extract_song_information_from_rs_dir(cdlc_file_name)
    #         self.songs.loaded_into_rs_with_song_data.add(song_data)
    #
    #         if is_not_empty(self.songs.missing_from_archive):
    #             self.songs.missing_from_archive.discard(cdlc_file_name)
    #
    #     log.info('Song data for the %s into Rocksmith loaded CDLC files were extracted.', len(cdlc_files))

    # def __extract_song_information_from_rs_dir(self, cdlc_file_name: str):
    #     return self.__extract_song_information(self.rocksmith_cdlc_dir, cdlc_file_name)

    # def __extract_song_information_from_archive_dir(self, cdlc_file_name: str):
    #     return self.__extract_song_information(self.cdlc_archive_dir, cdlc_file_name)

    @staticmethod
    def __extract_song_information(directory, cdlc_file_name: str):
        song_data = SongData()
        # TODO set cdlc_file_name into song_data here, or earlier? Or even later?
        song_data.song_file_name = cdlc_file_name
        file_path_to_extract = os.path.join(directory, cdlc_file_name)

        psarc_reader.extract_psarc(file_path_to_extract, song_data)

        # TODO write_to_file is True here, to keep the json in the cache. Is this not always True?
        # psarc_reader.extract_psarc(file_path_to_extract, song_data, True)
        # if LOG_DEBUG_IS_ENABLED:
        #     psarc_reader.extract_psarc(file_path_to_extract, song_data, True)
        # else:
        #     psarc_reader.extract_psarc(file_path_to_extract, song_data)

        return song_data

    # TODO refactor this. it should be like
    # - get_requests from RS playlist
    # - get filenames from DB
    # - move files
    def __move_requested_cdlc_files_from_archive_to_rs(self):

        if is_empty(self.songs.songs_from_archive_need_to_be_loaded):
            log.info("---- No file found to move from archive under the game.")
            return

        # TODO RS és ARCHIVUM könyvtárakban keresni a requested song után.
        #  És ha RS alatt van, akkor LOADED tag-et neki!
        #  Ha Archivum alatt, moveolni
        #  Ha sehol, akkor épp töltődik. Várni kell tag, vagy loading tag, ilyesmi

        log.info("---- Files to move from archive according to the requests: %s",
                 str(self.songs.songs_from_archive_need_to_be_loaded))

        actually_loaded_songs = set()
        for song_data in self.songs.songs_from_archive_need_to_be_loaded:
            if song_data.song_file_name in self.songs.loaded_into_rs:

                if self.rspl_tags.tag_loaded not in song_data.tags:
                    self.__set_tag_loaded(song_data)
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

        if is_not_empty(actually_loaded_songs):
            log.warning("---- Files newly moved and will be parsed: %s", str(actually_loaded_songs))
        if is_not_empty(self.songs.missing_from_archive):
            log.error("---- Missing files but found in Database: %s", str(self.songs.missing_from_archive))

    # TODO refactor this and move parts or the complete method into song_loader_helper.py
    def __find_existing_song_filenames_from_db_according_to_the_requests(self):
        for sr in self.rsplaylist["playlist"]:
            rspl_request_id = sr['id']
            for dlc_set in sr["dlc_set"]:
                rspl_song_id = dlc_set['id']
                cdlc_id = dlc_set["cdlc_id"]
                artist = dlc_set["artist"]
                title = dlc_set["title"]
                official = dlc_set["official"]
                rspl_position = str(sr["position"])

                # TODO #113 some ODLC-s were here not skipped! Maybe different official id?
                if is_official(official):
                    log.info("Skipping ODLC request with cdlc_id=%s - %s - %s", cdlc_id, artist, title)
                    continue

                songs_in_the_db = self.db_manager.search_song_in_the_db(artist, title)

                if is_empty(songs_in_the_db):
                    log.info("User must download the song: cdlc_id=%s - %s - %s", cdlc_id, artist, title)
                    rs_playlist.set_tag_to_download(self.twitch_channel,
                                                    self.phpsessid,
                                                    rspl_request_id,
                                                    self.rspl_tags)
                    continue

                for song_file_name in songs_in_the_db:
                    # TODO if it is possible, do not create always a new SongData.
                    #  If it is already exists, just reuse it, just search in a list
                    song_data = SongData(rspl_request_id, cdlc_id, rspl_song_id, artist, title, song_file_name)
                    song_data.rspl_official = official
                    song_data.rspl_position = rspl_position

                    # TODO is this really needed? It just updates tags in song data
                    update_tags_in_song_data(song_data, sr)

                    song_data.rspl_official = official
                    song_data.rspl_position = rspl_position

                    self.songs.requested_songs_found_in_db.add(song_file_name)
                    self.songs.requested_songs_found_in_db_with_song_data.add(song_data)  # TODO is this really needed?

                    log.debug("Request: %s", song_data)

        log.warning("Existing songs found: %s", repr_in_multi_line(self.songs.requested_songs_found_in_db))

    def __calculate_songs_need_to_be_moved_from_archive_to_under_rs(self):
        log.info("Calculating songs need to be moved from the archive according to the requests")

        # TODO read always the dir, or just use the list from songs?
        filenames_from_rs_dir = self.__get_cdlc_filenames_from_rs_dir()
        difference = self.songs.requested_songs_found_in_db.difference(filenames_from_rs_dir)

        self.songs.songs_from_archive_need_to_be_loaded = set()
        for song_data in set(self.songs.requested_songs_found_in_db_with_song_data):
            if song_data.song_file_name in filenames_from_rs_dir:
                log.info("Already loaded song: cdlc_id=%s - %s - %s",
                         song_data.cdlc_id, song_data.artist, song_data.title)
                if self.rspl_tags.tag_loaded not in song_data.tags:
                    rs_playlist.set_tag_loaded(self.twitch_channel,
                                               self.phpsessid,
                                               song_data.rspl_request_id,
                                               self.rspl_tags)

            elif song_data.song_file_name in difference:
                self.songs.songs_from_archive_need_to_be_loaded.add(song_data)

        log.info("Songs need to be moved from the archive according to the requests: %s",
                 str(self.songs.songs_from_archive_need_to_be_loaded))

    def __set_tag_loaded(self, song_data):
        rs_playlist.set_tag_loaded(self.twitch_channel,
                                   self.phpsessid,
                                   song_data.rspl_request_id,
                                   self.rspl_tags)
        song_data.tags.add(self.rspl_tags.tag_loaded)
        # song_data.tags.discard('need to download')  # TODO
