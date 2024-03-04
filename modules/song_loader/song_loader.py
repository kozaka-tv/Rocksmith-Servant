import logging
import os
import sqlite3
from time import time

from modules.song_loader.song_data import SongData
from modules.song_loader.song_loader_utils import log_loaded_cdlc_files, playlist_does_not_changed, update_tags, \
    check_cdlc_archive_dir, check_rocksmith_cdlc_dir
from modules.song_loader.songs import Songs
from utils import file_utils, rs_playlist, psarc_reader
from utils.db_utils import search_song_in_the_db
from utils.exceptions import RSPlaylistNotLoggedInError, BadDirectoryError
from utils.rs_playlist import get_playlist, is_user_not_logged_in

DEFAULT_CDLC_DIR = 'import'
HEARTBEAT = 5

con = sqlite3.connect('./servant.db')

log = logging.getLogger()


class SongLoader:
    def __init__(self, config_data):
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

            self.last_run = time()

            self.songs = Songs()

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
        file_utils.create_directory_logged(self.cdlc_dir)
        file_utils.create_directory_logged(self.cdlc_archive_dir)
        file_utils.create_directory_logged(self.rocksmith_cdlc_dir)

    def run(self):
        if self.enabled:
            if time() - self.last_run >= HEARTBEAT:
                # log.info("Load songs according to the requests!")

                if self.update_playlist():
                    log.info("Playlist has been changed, update songs!")
                    self.update_under_rs_loaded_cdlc_files()

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

    def update_under_rs_loaded_cdlc_files(self):
        for loaded_cdlc_file in self.cdlc_files_under_rs_dir():
            self.songs.loaded_into_rs.add(loaded_cdlc_file)
            self.extract_song_information(loaded_cdlc_file)
            if len(self.songs.missing_from_archive) > 0:
                self.songs.missing_from_archive.discard(loaded_cdlc_file)

    def extract_song_information(self, loaded_cdlc_file):
        song_data = SongData()
        filename_to_extract = os.path.join(self.rocksmith_cdlc_dir, loaded_cdlc_file)
        psarc_reader.extract_psarc(filename_to_extract, song_data, True)
        self.songs.loaded_into_rs_with_song_data.add(song_data)

    def cdlc_files_under_rs_dir(self):
        cdlc_files = file_utils.get_file_names_from(self.rocksmith_cdlc_dir)

        log_loaded_cdlc_files(cdlc_files)

        return cdlc_files

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

                with con:
                    rows = search_song_in_the_db(artist, title)

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

                con.commit()

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
