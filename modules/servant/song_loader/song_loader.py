import logging
import os
from time import time

from dacite import from_dict

from common.definitions import PSARC_INFO_FILE_CACHE_DIR, TMP_DIR
from config.config_data import ConfigData
from modules.servant.database.db_manager import DBManager
from modules.servant.song_loader.rs_playlist_data import RsPlaylist
from modules.servant.song_loader.song_data import SongData, ArtistTitle
from modules.servant.song_loader.song_loader_helper import check_cdlc_archive_dir, \
    check_rocksmith_cdlc_dir, update_tags_in_song_data, is_official, log_new_songs_found, playlist_does_not_changed
from modules.servant.tag_manager import tag_utils
from utils import file_utils, psarc_reader
from utils.collection_utils import is_collection_not_empty, is_collection_empty, repr_in_multi_line
from utils.exceptions import BadDirectoryError
from utils.exceptions import RSPLNotLoggedInError
from utils.rs_playlist_util import (get_playlist,
                                    user_is_not_logged_in,
                                    set_tag_to_download,
                                    unset_user_tags, set_tag_loaded)
from utils.string_utils import time_float_to_string

HEARTBEAT = 5

log = logging.getLogger()


class SongLoader:
    def __init__(self, config_data: ConfigData, songs):
        self.enabled = config_data.song_loader.enabled
        if self.enabled:
            self.twitch_channel = config_data.song_loader.twitch_channel
            self.phpsessid = config_data.song_loader.phpsessid

            self.rsplaylist = None
            self.rsplaylist_json = None
            self.rsplaylist_updated = True
            # TODO Shouldn't we activate the tag manager here and load it? Or just set it to none?
            self.rspl_tags = config_data.song_loader.rspl_tags

            self.rsplaylist_request_strings = set()

            self.cdlc_archive_dir = check_cdlc_archive_dir(config_data.song_loader.cdlc_archive_dir)
            self.destination_dir = config_data.song_loader.destination_dir
            self.download_dirs = config_data.file_manager.download_dirs
            self.rocksmith_cdlc_dir = check_rocksmith_cdlc_dir(config_data.song_loader.rocksmith_cdlc_dir)
            self.allow_load_when_in_game = config_data.song_loader.allow_load_when_in_game

            self.__create_directories()

            self.db_manager = None
            self.songs = songs

            self.last_run = None

    def set_db_manager(self, db_manager: DBManager):
        self.db_manager = db_manager

    def update_config(self, config_data):
        self.enabled = config_data.song_loader.enabled
        self.rspl_tags = config_data.song_loader.rspl_tags
        self.cdlc_archive_dir = check_cdlc_archive_dir(config_data.song_loader.cdlc_archive_dir)
        self.destination_dir = config_data.song_loader.destination_dir
        self.rocksmith_cdlc_dir = check_rocksmith_cdlc_dir(config_data.song_loader.rocksmith_cdlc_dir)
        self.allow_load_when_in_game = config_data.song_loader.allow_load_when_in_game
        self.phpsessid = config_data.song_loader.phpsessid

        self.__create_directories()

    def __create_directories(self):
        try:
            file_utils.create_directory_logged(TMP_DIR)
            file_utils.create_directory_logged(PSARC_INFO_FILE_CACHE_DIR)
            file_utils.create_directory_logged(self.cdlc_archive_dir)
            file_utils.create_directory_logged(self.rocksmith_cdlc_dir)
        except FileNotFoundError as bde:
            log.error("---------------------------------------")
            log.error("Directory %s could not be created!", bde.filename)
            log.error("Please fix the configuration!")
            log.error("---------------------------------------")
            raise BadDirectoryError from bde

    def run(self):
        if self.enabled:

            self.__init_and_cleanup_songs_data_at_first_run()

            time_waited = time() - self.last_run

            if time_waited >= HEARTBEAT:

                updated_songs_count = self.__update_songs_from_rs_dir()

                if self.__update_playlist_and_get_playlist_has_been_changed() or updated_songs_count > 0:
                    log.info("Playlist has been changed, update songs!")

                    self.__find_existing_song_filenames_from_db_according_to_the_requests()
                    self.__calculate_songs_need_to_be_moved_from_archive_to_under_rs()
                    self.__move_requested_cdlc_files_from_archive_to_rs()

                else:
                    log.info("No rsplaylist change, nothing to do...")

                self.last_run = time()
            else:
                log.debug("Waiting for heartbeat ... waited: %s seconds", time_float_to_string(time_waited))

    # def __update_songs_from_download_dir(self):
    #     cdlc_files = file_utils.get_files_from_directories(self.download_dirs)
    #     for source_dir in self.download_dirs:
    #         self.__store_and_return_all_the_new_song_datas(source_dir, self.songs.songs_in_tmp)

    def __update_songs_from_rs_dir(self) -> int:
        updated_songs_count = self.__store_and_return_all_the_new_song_datas(
            self.rocksmith_cdlc_dir, self.songs.songs_in_rs)
        if updated_songs_count > 0:
            log.debug("Count of songs updated from RS dir: %s", updated_songs_count)
        return updated_songs_count

    # def __update_songs_from_import_dir(self):
    #     self.__store_and_return_all_the_new_song_datas(self.destination_dir, self.songs.songs_in_import)

    # def __update_songs_from_tmp_dir(self):
    #     self.__store_and_return_all_the_new_song_datas(self.destination_dir, self.songs.songs_in_tmp)

    def __update_playlist_and_get_playlist_has_been_changed(self):
        is_initial_load = self.rsplaylist_json is None
        new_playlist = get_playlist(self.twitch_channel, self.phpsessid)

        self.__update_rsplaylist_with(new_playlist)
        self.__stop_if_user_is_not_logged_in_on_rspl_page(new_playlist)

        if is_initial_load:
            self.__handle_initial_playlist_load()
            return True

        new_rsplaylist_request_strings = self.__extract_request_strings()
        if playlist_does_not_changed(self.rsplaylist_request_strings, new_rsplaylist_request_strings):
            return False

        log.info("Playlist has been changed, lets update!")
        self.rsplaylist_request_strings = self.__extract_request_strings()
        return True

    def __extract_request_strings(self):
        return {item.string for item in self.rsplaylist.playlist}

    def __handle_initial_playlist_load(self):
        log.info("Initial load of the playlist is done...")
        tag_utils.validate_and_log_rspl_tags(self.rsplaylist.channel_tags, self.rspl_tags)

    def __update_rsplaylist_with(self, new_playlist):
        self.rsplaylist_json = new_playlist
        self.rsplaylist = from_dict(data_class=RsPlaylist, data=new_playlist)

    def __stop_if_user_is_not_logged_in_on_rspl_page(self, new_playlist):
        not_logged_in = user_is_not_logged_in(new_playlist)

        if not_logged_in is None:
            log.debug("Playlist is empty! Can not tell, that the user is logged in or not!")

        elif not_logged_in:
            self.rsplaylist_json = None
            self.last_run = time()
            log.error("User is not logged in! Please log in on RSPL!")
            raise RSPLNotLoggedInError

        else:
            log.debug("User is logged in and there is at least one request on the list.")

    def __init_and_cleanup_songs_data_at_first_run(self):
        if self.last_run is None:
            self.last_run = time()

            log.warning('Initialising and cleaning up all CDLC file information')

            filenames_from_archive_dir = self.__get_cdlc_filenames_from_archive_dir()
            filenames_from_rs_dir = self.__get_cdlc_filenames_from_rs_dir()

            self.__clean_up_archive_dir_for_duplicates(filenames_from_rs_dir, filenames_from_archive_dir)

            filenames_in_rs_and_archive_dir = filenames_from_rs_dir.union(filenames_from_archive_dir)
            filenames_in_db = self.db_manager.all_song_filenames()
            self.__clean_up_songs_in_db(filenames_in_rs_and_archive_dir, filenames_in_db)

            self.__store_and_return_all_the_new_song_datas(self.cdlc_archive_dir, self.songs.songs_in_archive)
            self.__store_and_return_all_the_new_song_datas(self.rocksmith_cdlc_dir, self.songs.songs_in_rs)

            log.info('Count of songs in archive: %s', len(self.songs.songs_in_archive))
            log.info('Count of songs in rs: %s', len(self.songs.songs_in_rs))

    def __get_cdlc_filenames_from_archive_dir(self):
        return file_utils.get_file_names_from(self.cdlc_archive_dir)

    def __get_cdlc_filenames_from_rs_dir(self):
        return file_utils.get_file_names_from(self.rocksmith_cdlc_dir)

    def __clean_up_archive_dir_for_duplicates(self, filenames_from_rs_dir, filenames_from_archive_dir):
        log.info('Cleaning up archive dir for duplicates')
        duplicates = set(filenames_from_rs_dir).intersection(filenames_from_archive_dir)
        if is_collection_not_empty(duplicates):
            self.__remove_duplicates(duplicates, filenames_from_archive_dir)

    def __clean_up_songs_in_db(self, filenames_in_rs_and_archive_dir, filenames_in_db):
        log.info('Cleaning up songs in DB')
        to_delete = filenames_in_db.difference(filenames_in_rs_and_archive_dir)
        if is_collection_not_empty(to_delete):
            log.info("Count of songs to be deleted: %s", len(to_delete))
            self.db_manager.delete_song_by_filename(to_delete)

            for filename_to_delete in to_delete:
                log.debug("Song has been deleted: %s", filename_to_delete)
                filenames_in_db.discard(filename_to_delete)

    def __remove_duplicates(self, duplicates, filenames_from_archive_dir):
        log.warning("Duplicated CDLC files found in the archive and under RS! Files to be deleted from the archive: %s",
                    duplicates)
        for filename in duplicates:
            file_utils.delete_file(self.cdlc_archive_dir, filename)
            filenames_from_archive_dir.remove(filename)

    def __store_and_return_all_the_new_song_datas(self, directory, songs_to_update: dict):
        log.info('Loading songs from directory: %s', directory)

        new_songs_count = 0
        songs = {}

        filenames = file_utils.get_file_names_from(directory)

        songs_removed = self.__remove_missing_songs_from(songs_to_update, filenames)
        log.debug('songs_removed:%s', repr_in_multi_line(songs_removed))

        new_songs = filenames.difference(songs_to_update)
        log_new_songs_found(new_songs)

        for filename in filenames:
            if filename not in songs_to_update:
                song_data = self.db_manager.search_song_by_filename(filename)

                if song_data is None:
                    song_data = self.__extract_song_information(directory, filename)
                    self.db_manager.insert_song(song_data)
                    new_songs_count += 1
                    log.info('New song added to DB: %s', song_data)

                songs.update({song_data.song_filename: song_data})
                if log.isEnabledFor(logging.DEBUG) and len(songs) % 100 == 0:
                    log.info("Loaded %s songs...", len(songs))

        songs_to_update.update(songs)

        if new_songs_count > 0:
            log.info("---- Loaded %s songs, and from this, %s new song(s) stored in DB", len(songs), new_songs_count)
            return new_songs_count

        log.debug("---- No new songs were loaded!")
        return 0

    @staticmethod
    def __remove_missing_songs_from(songs_to_update: dict[str, SongData](), filenames):
        removed = dict[str, SongData]()

        missing = set(songs_to_update).difference(filenames)

        if missing:
            log.debug('Missing songs will be removed: %s', missing)

            for missing_song in missing:
                pop = songs_to_update.pop(missing_song, None)
                removed[pop.song_filename] = pop

        return removed

    @staticmethod
    def __extract_song_information(directory, cdlc_file_name: str):
        song_data = SongData(song_filename=cdlc_file_name)

        file_path_to_extract = os.path.join(directory, cdlc_file_name)

        psarc_reader.extract(file_path_to_extract, song_data)

        return song_data

    def __move_requested_cdlc_files_from_archive_to_rs(self):
        if is_collection_empty(self.songs.songs_from_archive_has_to_be_moved):
            log.debug("---- No file found to move from archive to RS directory.")
            return

        log.info("---- Files to move from archive according to the requests: %s",
                 repr_in_multi_line(self.songs.songs_from_archive_has_to_be_moved))

        actually_loaded_songs = set()
        for filename, song_data in list(self.songs.songs_from_archive_has_to_be_moved.items()):

            if self.__song_already_moved_from_archive(filename):
                if self.__has_no_tag_loaded(song_data):
                    self.__set_tag_loaded(song_data)

            else:
                song_to_move = os.path.join(self.cdlc_archive_dir, filename)
                moved = file_utils.move_file(song_to_move, self.destination_dir)
                if moved:
                    log.info("The song were moved from the archive into RS directory. Moved file: %s", song_to_move)
                    self.songs.moved_from_archive.update(
                        {filename: self.songs.songs_from_archive_has_to_be_moved.pop(filename)})
                    actually_loaded_songs.add(filename)
                    set_tag_loaded(self.twitch_channel,
                                   self.phpsessid,
                                   song_data.rspl_request_id,
                                   self.rspl_tags)
                else:
                    log.error("Could not move file! Song exists in DB, but there is no file in archive: %s",
                              song_to_move)
                    self.songs.missing_from_archive.update(
                        {filename: self.songs.songs_from_archive_has_to_be_moved.pop(filename)})

                    if self.__has_no_tag_to_download(song_data):
                        set_tag_to_download(self.twitch_channel,
                                            self.phpsessid,
                                            song_data.rspl_request_id,
                                            self.rspl_tags)

        if is_collection_not_empty(self.songs.moved_from_archive):
            log.warning("---- Files newly moved and will be parsed: %s", str(actually_loaded_songs))
        if is_collection_not_empty(self.songs.missing_from_archive):
            log.error("---- Missing files but found in Database: %s", str(self.songs.missing_from_archive))

    def __song_already_moved_from_archive(self, filename):
        return filename in self.songs.moved_from_archive

    def __has_no_tag_loaded(self, song_data):
        return self.rspl_tags.tag_loaded not in song_data.tags

    def __has_no_tag_to_download(self, song_data):
        return self.rspl_tags.tag_to_download not in song_data.tags

    @staticmethod
    def __no_file_found_in_db_for_this_song(songs_in_the_db):
        return is_collection_empty(songs_in_the_db)

    def __find_existing_song_filenames_from_db_according_to_the_requests(self):
        playlist = self.rsplaylist.playlist
        for playlist_item in playlist:
            dlc_items_count = len(playlist_item.dlc_set)
            officials_count = 0
            to_download_count = 0
            loaded_count = 0
            log.debug("Number of items in dlc_set for playlist_item position=%s id=%s dlc_items_count=%s",
                      playlist_item.position, playlist_item.id, dlc_items_count)

            for dlc_set_item in playlist_item.dlc_set:
                cdlc_id = dlc_set_item.cdlc_id
                artist = dlc_set_item.artist
                title = dlc_set_item.title
                log.debug("Searching for --> cdlc_id=%s | %s - %s", cdlc_id, artist, title)

                official = dlc_set_item.official
                if is_official(official):
                    officials_count += 1
                    log.debug("Skipping ODLC request with cdlc_id=%s - %s - %s", cdlc_id, artist, title)
                    continue

                songs_in_the_db = self.db_manager.search_song_by_artist_and_title(artist, title)

                rspl_position = str(playlist_item.position)

                if self.__no_file_found_in_db_for_this_song(songs_in_the_db):
                    to_download_count += 1
                    log.debug("This must be downloaded --> cdlc_id=%s - %s - %s", cdlc_id, artist, title)
                    continue

                loaded_count += 1
                for song_filename in songs_in_the_db:
                    song_data = SongData(song_filename=song_filename,
                                         artist_title=ArtistTitle(artist, title),
                                         rspl_request_id=playlist_item.id,
                                         cdlc_id=cdlc_id,
                                         rspl_song_id=dlc_set_item.id,
                                         rspl_official=official,
                                         rspl_position=rspl_position)

                    update_tags_in_song_data(song_data, playlist_item)

                    self.songs.requested_songs_found_in_db.update({song_data.song_filename: song_data})

                    log.info("Request found in DB: %s", song_data)

            # if any tag has to set
            if officials_count > 0 or to_download_count > 0 or loaded_count > 0:
                log.debug(
                    "Unset tags, as tags may be actualised! officials_count=%s to_download_count=%s loaded_count=%s ",
                    officials_count, to_download_count, loaded_count)
                unset_user_tags(self.twitch_channel,
                                self.phpsessid,
                                playlist_item.id,
                                self.rspl_tags,
                                playlist_item.tags)

            if to_download_count > 0:
                log.debug("To-download count: %s", to_download_count)
                set_tag_to_download(self.twitch_channel,
                                    self.phpsessid,
                                    playlist_item.id,
                                    self.rspl_tags)

            if loaded_count > 0:
                log.debug("Loaded count: %s", to_download_count)
                set_tag_loaded(self.twitch_channel,
                               self.phpsessid,
                               playlist_item.id,
                               self.rspl_tags)

        if is_collection_not_empty(self.songs.requested_songs_found_in_db):
            log.info("Existing songs found: %s", repr_in_multi_line(self.songs.requested_songs_found_in_db))

    def __calculate_songs_need_to_be_moved_from_archive_to_under_rs(self):
        log.debug("Calculating songs hast to be moved from the archive according to the requests")

        filenames_from_rs_dir = self.__get_cdlc_filenames_from_rs_dir()
        difference = set(self.songs.requested_songs_found_in_db).difference(filenames_from_rs_dir)

        self.songs.songs_from_archive_has_to_be_moved = dict[str, SongData]()
        for filename, song_data in self.songs.requested_songs_found_in_db.items():
            if filename in filenames_from_rs_dir:
                log.debug("Already loaded song: %s", song_data)
                if self.__has_no_tag_loaded(song_data):
                    set_tag_loaded(self.twitch_channel,
                                   self.phpsessid,
                                   song_data.rspl_request_id,
                                   self.rspl_tags)

            elif filename in difference:
                self.songs.songs_from_archive_has_to_be_moved.update({filename: song_data})

        if is_collection_not_empty(self.songs.songs_from_archive_has_to_be_moved):
            log.info("Songs from archive has to be moved according to the requests: %s",
                     repr_in_multi_line(self.songs.songs_from_archive_has_to_be_moved))

    def __set_tag_loaded(self, song_data):
        set_tag_loaded(self.twitch_channel,
                       self.phpsessid,
                       song_data.rspl_request_id,
                       self.rspl_tags)
        song_data.tags.add(self.rspl_tags.tag_loaded)
