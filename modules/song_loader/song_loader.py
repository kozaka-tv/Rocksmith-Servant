import logging
import os
import sqlite3
from time import time

from deepdiff import DeepDiff

from modules.song_loader.song_data import SongData
from modules.song_loader.songs import Songs
from utils import file_utils, rs_playlist, string_utils, db_utils
from utils.exceptions import ConfigError, RSPlaylistNotLoggedInError, BadDirectoryError
from utils.rs_playlist import get_playlist

NL = os.linesep

ERR_MSG_CDLC_ARCHIVE_DIR = "Please set your CDLC archive directory in the config!" + NL + \
                           "This is the directory, where you normally store all of your downloaded CDLC files."

ERR_MSG_ROCKSMITH_CDLC_DIR = "Please set your Rocksmith CDLC directory!" + NL + \
                             "This is the directory, where you normally store all of your CDLC files what you play" \
                             "in the game."

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
            self.cdlc_archive_dir = self.check_cdlc_archive_dir(config_data.song_loader.cdlc_archive_dir)
            self.destination_directory = config_data.song_loader.destination_directory
            self.rocksmith_cdlc_dir = self.check_rocksmith_cdlc_dir(config_data.song_loader.rocksmith_cdlc_dir)
            self.allow_load_when_in_game = config_data.song_loader.allow_load_when_in_game
            self.cdlc_import_json_file = config_data.song_loader.cdlc_import_json_file
            self.songs_to_load = os.path.join(config_data.song_loader.cdlc_dir, config_data.song_loader.cfsm_file_name)

            try:
                self.create_directories()
            except FileNotFoundError as bde:
                log.error("---------------------------------------")
                log.error(f"Directory {bde.filename} could not be created!")
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
        self.cdlc_archive_dir = self.check_cdlc_archive_dir(config_data.song_loader.cdlc_archive_dir)
        self.destination_directory = config_data.song_loader.destination_directory
        self.rocksmith_cdlc_dir = self.check_rocksmith_cdlc_dir(config_data.song_loader.rocksmith_cdlc_dir)
        self.allow_load_when_in_game = config_data.song_loader.allow_load_when_in_game
        self.phpsessid = config_data.song_loader.phpsessid
        self.cdlc_import_json_file = config_data.song_loader.cdlc_import_json_file
        self.songs_to_load = os.path.join(config_data.song_loader.cdlc_dir, config_data.song_loader.cfsm_file_name)

        self.create_directories()

    @staticmethod
    def check_cdlc_archive_dir(cdlc_archive_dir):
        if cdlc_archive_dir is None or cdlc_archive_dir.startswith('<Enter your'):
            raise ConfigError(ERR_MSG_CDLC_ARCHIVE_DIR)
        return os.path.join(cdlc_archive_dir)

    @staticmethod
    def check_rocksmith_cdlc_dir(rocksmith_cdlc_dir):
        if rocksmith_cdlc_dir is None or rocksmith_cdlc_dir.startswith('<Enter your'):
            raise ConfigError(ERR_MSG_ROCKSMITH_CDLC_DIR)
        return os.path.join(rocksmith_cdlc_dir)

    def create_directories(self):
        file_utils.create_directory(self.cdlc_dir)
        file_utils.create_directory(self.cdlc_archive_dir)
        file_utils.create_directory(self.rocksmith_cdlc_dir)

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

        self.exit_if_user_not_logged_in(new_playlist)

        if self.rsplaylist is None:
            log.debug("Initial load of the rsplaylist done...")
            self.rsplaylist = new_playlist
            return True

        if self.playlist_does_not_changed(new_playlist):
            return False

        log.info("Playlist has been changed, lets update!")

        self.rsplaylist = new_playlist

        return True

    def playlist_does_not_changed(self, new_playlist):
        diff = DeepDiff(self.rsplaylist, new_playlist, exclude_regex_paths="\\['inactive_time'\\]")
        if str(diff) == "{}":
            log.debug("Playlist does not changed!")
            return True

        log.debug(f"Playlist has been changed! Diffs: {diff}")
        return False

    def exit_if_user_not_logged_in(self, new_playlist):
        for sr in new_playlist["playlist"]:
            for cdlc in sr["dlc_set"]:
                if self.is_user_not_logged_in(cdlc):
                    self.rsplaylist = None
                    self.last_run = time()
                    log.error("User must be logged in into RS playlist to be able to use the module!")
                    raise RSPlaylistNotLoggedInError
                else:
                    return

    def update_under_rs_loaded_cdlc_files(self):
        loaded_cdlc_files = self.scan_cdlc_files_under_rs_dir()
        for loaded_cdlc_file in loaded_cdlc_files:
            self.songs.loaded_into_rs.add(loaded_cdlc_file)
            if len(self.songs.missing_from_archive) > 0:
                self.songs.missing_from_archive.discard(loaded_cdlc_file)

    def scan_cdlc_files_under_rs_dir(self):
        cdlc_files = file_utils.get_file_names_from(self.rocksmith_cdlc_dir)

        if len(cdlc_files) > 0:
            self.log_loaded_cdlc_files(cdlc_files)

        return cdlc_files

    @staticmethod
    def log_loaded_cdlc_files(cdlc_files):
        log.info(f'Found {len(cdlc_files)} into Rocksmith loaded CDLC files.')

        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"---------- The {len(cdlc_files)} files already loaded into Rocksmith:")
            for cdlc_file in cdlc_files:
                log.debug(cdlc_file)
            log.debug("-----------------------------")

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
                #   search in a list
                song_data = SongData(rspl_request_id, cdlc_id, rspl_song_id, artist, title)
                song_data.rspl_official = dlc_set["official"]
                song_data.rspl_position = str(sr["position"])
                log.info(f"Request: {song_data}")

                self.update_tags(song_data, sr)

                # Do not load official DLC files
                if song_data.is_official:  # TODO #113 some ODLC-s were here not skipped! Maybe different official id?
                    log.debug(f"Skipping ODLC: {song_data}")
                    continue

                with con:
                    rows = self.search_song_in_the_db(artist, title)

                    if len(rows) > 0:
                        log.debug(f"---- sr {song_data.rspl_position} -------")
                        for element in rows:
                            song_file_name = str(element[0])
                            song_data.song_file_name = song_file_name

                            log.debug(f"row={song_file_name}")
                            self.songs.song_data_set.add(song_data)
                    else:
                        log.debug(f"User must download the song: cdlc_id={cdlc_id} - {artist} - {title}")
                        # rs_playlist.set_tag_to_download(self.twitch_channel,
                        #                                 self.phpsessid,
                        #                                 song_data.rspl_request_id,
                        #                                 self.rspl_tags)

                con.commit()

        if len(self.songs.song_data_set) <= 0:
            # TODO actually this is not true. Only, just no file was moved from archive into the game.
            log.info("---- The rsplaylist is empty, nothing to move!")
            return

        log.info(f"---- Files to move from archive according to the requests: {str(self.songs.song_data_set)}")

        actually_loaded_songs = set()
        for song_data in self.songs.song_data_set:
            if song_data.song_file_name in self.songs.loaded_into_rs:

                if self.rspl_tags.tag_loaded not in song_data.tags:
                    rs_playlist.set_tag_loaded(self.twitch_channel,
                                               self.phpsessid,
                                               song_data.rspl_request_id,
                                               self.rspl_tags)
                    song_data.tags.add(self.rspl_tags.tag_loaded)
                    # song_data.tags.discard('need to download')  # TODO
            else:
                song_to_move = os.path.join(self.cdlc_archive_dir, song_data.song_file_name)
                moved = file_utils.move_file(song_to_move, self.destination_directory)
                if moved:
                    log.debug(f"The song were moved from the archive to under RS. Moved file: {song_to_move}")
                    self.songs.loaded_into_rs.add(song_data.song_file_name)
                    actually_loaded_songs.add(song_data.song_file_name)
                    # TODO this takes 1 sec for each call. If we have a list of 30 songs, it could take 30 seconds!
                    #   Do it only once!
                    rs_playlist.set_tag_loaded(self.twitch_channel,
                                               self.phpsessid,
                                               song_data.rspl_request_id,
                                               self.rspl_tags)
                else:
                    log.debug(f"Could not move file: {song_to_move}")
                    self.songs.missing_from_archive.add(song_data.song_file_name)
                    # TODO this takes 1 sec for each call. If we have a list of 30 songs, it could take 30 seconds!
                    #   Do it only once!
                    rs_playlist.set_tag_to_download(self.twitch_channel, self.phpsessid, song_data.rspl_request_id,
                                                    self.rspl_tags)

        if len(actually_loaded_songs) > 0:
            log.warning(f"---- Files newly moved and will be parsed: {str(actually_loaded_songs)}")
        if len(self.songs.missing_from_archive) > 0:
            log.error(f"---- Missing files but found in Database: {str(self.songs.missing_from_archive)}")

    @staticmethod
    def is_user_not_logged_in(cdlc):
        try:
            cdlc['id']
        except TypeError:
            return True
        return False

    @staticmethod
    def update_tags(song_data, sr):
        song_data.tags.clear()
        for tag in sr['tags']:
            song_data.tags.add(tag)

    @staticmethod
    def search_song_in_the_db(artist, title):
        rows = db_utils.get_songs_from_db(artist, title)
        # TODO hm...maybe remove special chars and do a second query. To load all possible variations?
        # TODO make a special search for similar words in artist and title
        # So not only if len(rows) <= 0
        if len(rows) <= 0:
            # remove special chars
            artist_norm = string_utils.remove_special_chars(artist)
            title_norm = string_utils.remove_special_chars(title)
            rows = db_utils.get_songs_from_db(artist_norm, title_norm)
        return rows
