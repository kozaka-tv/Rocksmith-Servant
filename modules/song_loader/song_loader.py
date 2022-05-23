import os
import sqlite3

import unicodedata
from deepdiff import DeepDiff
from time import time

from modules.song_loader.song_data import SongData, Songs
from utils import logger, file_utils, rs_playlist
from utils.exceptions import ConfigError, RSPlaylistNotLoggedInError
from utils.rs_playlist import get_playlist

MODULE_NAME = "SongLoader"

NL = os.linesep

ERR_MSG_CDLC_ARCHIVE_DIR = "Please set your CDLC archive directory in the config!" + NL + \
                           "This is the directory, where you normally store all of your downloaded CDLC files."

ERR_MSG_ROCKSMITH_CDLC_DIR = "Please set your Rocksmith CDLC directory!" + NL + \
                             "This is the directory, where you normally store all of your CDLC files what you play" \
                             "in the game."

DEFAULT_CDLC_DIR = 'import'
HEARTBEAT = 5

con = sqlite3.connect('./servant.db')


class SongLoader:
    def __init__(self, enabled, phpsessid: str, cdlc_dir, cfsm_file_name, cdlc_archive_dir, destination_directory,
                 rocksmith_cdlc_dir, cdlc_import_json_file, allow_load_when_in_game=True):
        self.enabled = enabled
        if enabled:
            self.playlist = None
            self.playlist_updated = True
            self.cdlc_dir = os.path.join(cdlc_dir)
            self.cfsm_file_name = cfsm_file_name
            self.cdlc_archive_dir = self.check_cdlc_archive_dir(cdlc_archive_dir)
            self.destination_directory = destination_directory
            self.rocksmith_cdlc_dir = self.check_rocksmith_cdlc_dir(rocksmith_cdlc_dir)
            self.allow_load_when_in_game = allow_load_when_in_game
            self.phpsessid = rs_playlist.check_phpsessid(phpsessid)
            self.cdlc_import_json_file = cdlc_import_json_file

            self.songs_to_load = os.path.join(cdlc_dir, cfsm_file_name)
            # TODO maybe call this different...do we need this?
            self.raw_playlist = None

            self.create_directories()

            self.last_run = time()

        self.songs = Songs()

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
                logger.log("Load songs according to the requests!", MODULE_NAME)

                if self.update_playlist():
                    logger.log("Playlist has been changed, update songs!")
                    self.update_under_rs_loaded_cdlc_files()

                    # TODO or maybe this should be configurable?
                    # else:  # load songs only in case we are not in game to avoid lagging in game

                    self.move_requested_cdlc_files_to_destination()
                else:
                    # TODO Maybe, this is not completely true! If the file is not parsed, then it will be not checked.
                    #   I think, the logic must be separated.
                    #   1) rs playlist NOT updated --> Just check dirs and move files
                    #   2) rs playlist UPDATED --> check DB and move files
                    logger.log("No playlist change, nothing to do...", MODULE_NAME)

                self.last_run = time()

    def update_playlist(self):
        new_playlist = get_playlist(self.phpsessid)

        self.exit_if_user_not_logged_in(new_playlist)

        if self.playlist is None:
            logger.debug("Initial load of the playlist done...", MODULE_NAME)
            self.playlist = new_playlist
            return True

        diff = DeepDiff(self.playlist, new_playlist, exclude_regex_paths="\\['inactive_time'\\]")

        if str(diff) == "{}":
            return False

        logger.debug("Playlist has been changed! Diffs: {}".format(diff), MODULE_NAME)
        self.playlist = new_playlist

        return True

    def exit_if_user_not_logged_in(self, new_playlist):
        for sr in new_playlist["playlist"]:
            for cdlc in sr["dlc_set"]:
                if self.is_user_not_logged_in(cdlc):
                    self.playlist = None
                    self.last_run = time()
                    raise RSPlaylistNotLoggedInError
                else:
                    return

    def update_under_rs_loaded_cdlc_files(self):
        loaded_cdlc_files = self.scan_cdlc_files_under_rs_dir()
        for loaded_cdlc_file in loaded_cdlc_files:
            self.songs.loaded.add(loaded_cdlc_file)
            if len(self.songs.missing) > 0:
                self.songs.missing.discard(loaded_cdlc_file)

    def scan_cdlc_files_under_rs_dir(self):
        cdlc_files = file_utils.get_file_names_from(self.rocksmith_cdlc_dir)

        if len(cdlc_files) > 0:
            self.log_loaded_cdlc_files(cdlc_files)

        return cdlc_files

    @staticmethod
    def log_loaded_cdlc_files(cdlc_files):
        logger.log('Found {} into Rocksmith loaded CDLC files.'.format(len(cdlc_files)), MODULE_NAME)

        # logger.debug("---------- loaded CDLC files:", MODULE_NAME)
        # for cdlc_file in cdlc_files:
        #     logger.debug(cdlc_file, MODULE_NAME)
        # logger.debug("-----------------------------", MODULE_NAME)

    # TODO refactor this. it should be like
    # - get_requests from RS playlist
    # - get filenames from DB
    # - move files
    def move_requested_cdlc_files_to_destination(self):
        for sr in self.playlist["playlist"]:
            sr_id = sr['id']
            for cdlc in sr["dlc_set"]:
                rspl_id = cdlc['id']
                cdlc_id = cdlc["cdlc_id"]
                artist = cdlc["artist"]
                title = cdlc["title"]
                artist_title = str(rspl_id) + " - " + str(cdlc_id) + " - " + artist + " - " + title
                logger.log("Request " + artist_title + " will be managed.", MODULE_NAME)

                # TODO if it is possible, do not create always a new SongData. If it is already exists, just reuse it!
                #   search in a list
                song_data = SongData(sr_id, cdlc_id)
                self.update_tags(song_data, sr)

                # Do not load official DLC files
                if cdlc["official"] == 4:
                    logger.debug("Skipping ODLC " + artist_title, MODULE_NAME)
                    continue

                with con:
                    rows = self.search_song_in_the_db(artist, title)

                    if len(rows) > 0:
                        logger.debug("---- sr " + str(sr["position"]) + " -------", MODULE_NAME)
                        for element in rows:
                            song_file_name = str(element[0])
                            song_data.song_file_name = song_file_name

                            logger.debug("row=" + song_file_name, MODULE_NAME)
                            self.songs.song_data_set.add(song_data)
                    else:
                        logger.debug("User must download the song: cdlc_id={} - {} - {}".format(cdlc_id, artist, title),
                                     MODULE_NAME)
                        # rs_playlist.set_tag_to_download(self.phpsessid, song_data.sr_id)

                con.commit()

        if len(self.songs.song_data_set) <= 0:
            logger.warning("---- The playlist is empty, nothing to move!", MODULE_NAME)
            return

        logger.warning(
            "---- Files to move from archive according to the requests: " + str(self.songs.song_data_set),
            MODULE_NAME)

        actually_loaded_songs = set()
        for song_data in self.songs.song_data_set:
            if song_data.song_file_name in self.songs.loaded:
                # TODO this takes 1 sec for each call. If we have a list of 30 songs, it could take 30 seconds!
                #   Do it only once!
                if 'afea46a9' not in song_data.tags:
                    rs_playlist.set_tag_loaded(self.phpsessid, song_data.sr_id)
                    song_data.tags.add('afea46a9')
                    # song_data.tags.discard('need to download')  # TODO
            else:
                song_to_move = os.path.join(self.cdlc_archive_dir, song_data.song_file_name)
                moved = file_utils.move_file(song_to_move, self.destination_directory, MODULE_NAME)
                if moved:
                    logger.debug(
                        "The song were moved from the archive to under RS. Moved file: {}".format(song_to_move),
                        MODULE_NAME)
                    self.songs.loaded.add(song_data.song_file_name)
                    actually_loaded_songs.add(song_data.song_file_name)
                    # TODO this takes 1 sec for each call. If we have a list of 30 songs, it could take 30 seconds!
                    #   Do it only once!
                    rs_playlist.set_tag_loaded(self.phpsessid, song_data.sr_id)
                else:
                    logger.debug("Could not move file: {}".format(song_to_move), MODULE_NAME)
                    self.songs.missing.add(song_data.song_file_name)
                    # TODO this takes 1 sec for each call. If we have a list of 30 songs, it could take 30 seconds!
                    #   Do it only once!
                    rs_playlist.set_tag_to_download(self.phpsessid, song_data.sr_id)

        if len(actually_loaded_songs) > 0:
            logger.warning("---- Files newly moved and will be parsed: " + str(actually_loaded_songs), MODULE_NAME)
        if len(self.songs.missing) > 0:
            logger.error("---- Missing files but found in Database: " + str(self.songs.missing), MODULE_NAME)

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

    def search_song_in_the_db(self, artist, title):
        rows = self.get_song_from_db(artist, title)
        if len(rows) <= 0:
            # remove special chars
            artist_norm = self.remove_special_chars(artist)
            title_norm = self.remove_special_chars(title)
            rows = self.get_song_from_db(artist_norm, title_norm)
        return rows

    @staticmethod
    def remove_special_chars(text):
        # return unicodedata.normalize('NFD', text).encode('ascii', 'ignore')
        return ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')

    @staticmethod
    def get_song_from_db(artist, title):
        cur = con.cursor()
        # TODO add and colTagged != 'ODLC'?
        execute = cur.execute("SELECT distinct colFileName FROM songs where colArtist like ? and colTitle like ?",
                              ("%" + artist + "%", "%" + title + "%"))
        rows = execute.fetchall()
        return rows
