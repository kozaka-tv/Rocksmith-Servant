import os
import sqlite3
from time import time

import unicodedata

from modules.song_loader.song_data import SongData
from utils import logger, file_utils, rs_playlist
from utils.exceptions import ConfigError, RSPlaylistNotLoggedInError
from utils.rs_playlist import get_playlist

MODULE_NAME = "SongLoader"

NL = os.linesep

ERR_MSG_CDLC_ARCHIVE_DIR = "Please set your CDLC archive directory in the config!" + NL + \
                           "This is the directory, where you normally store all of your downloaded CDLC files."

ERR_MSG_ROCKSMITH_CDLC_DIR = "Please set your Rocksmith CDLC directory!" + NL + \
                             "This is the directory, where you normally store all of your CDLC files what you. play" \
                             "in the game."

DEFAULT_CDLC_DIR = 'import'
HEARTBEAT = 5

con = sqlite3.connect('./servant.db')


class SongLoader:
    def __init__(self, enabled, phpsessid: str, cdlc_dir, cfsm_file_name, cdlc_archive_dir, destination_directory,
                 rocksmith_cdlc_dir, cdlc_import_json_file, allow_load_when_in_game=True):
        self.enabled = enabled
        if enabled:
            self.cdlc_dir = os.path.join(cdlc_dir)
            self.cfsm_file_name = cfsm_file_name
            self.cdlc_archive_dir = self.check_cdlc_archive_dir(cdlc_archive_dir)
            self.destination_directory = destination_directory
            self.rocksmith_cdlc_dir = self.check_rocksmith_cdlc_dir(rocksmith_cdlc_dir)
            self.allow_load_when_in_game = allow_load_when_in_game
            self.phpsessid = rs_playlist.check_phpsessid(phpsessid)
            self.cdlc_import_json_file = cdlc_import_json_file

            self.songs_to_load = os.path.join(cdlc_dir, cfsm_file_name)
            self.first_run = True
            # TODO maybe call this different...do we need this?
            self.raw_playlist = None

            self.create_directories()

            self.last_run = time()

        self.loaded_songs = set()
        self.missing_songs = set()

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

    def load(self):
        if self.enabled:
            if self.first_run:
                # TODO this must be done
                logger.log("Try to load new songs for the CFSM file: {}".format(self.songs_to_load))
                self.first_run = False
                self.get_file_to_import()

            if time() - self.last_run >= HEARTBEAT:
                logger.warning("Load songs according to the requests!")
                self.update_under_rs_loaded_cdlc_files()

                # TODO or maybe this should be configurable?
                # else:  # load songs only in case we are not in game to avoid lagging in game
                self.move_requested_cdlcs_to_destination()

                self.last_run = time()

    def update_under_rs_loaded_cdlc_files(self):
        loaded_cdlc_files = self.scan_cdlc_files_under_rs_dir()
        for loaded_cdlc_file in loaded_cdlc_files:
            self.loaded_songs.add(loaded_cdlc_file)
            self.missing_songs.discard(loaded_cdlc_file)

    def get_file_to_import(self):
        path = file_utils.get_file_path(self.cdlc_dir, self.cfsm_file_name)
        logger.log('CFSM_file to load: {}'.format(path), MODULE_NAME)

    def scan_cdlc_files_under_rs_dir(self):
        cdlc_files = file_utils.get_file_names_from(self.rocksmith_cdlc_dir)

        if len(cdlc_files) > 0:
            self.log_loaded_cdlc_files(cdlc_files)

        return cdlc_files

    @staticmethod
    def log_loaded_cdlc_files(cdlc_files):
        logger.log('Found {} into Rocksmith loaded CDLC files.'.format(len(cdlc_files)), MODULE_NAME)

        # logger.debug("---------- loaded CDLC files:")
        # for cdlc_file in cdlc_files:
        #     logger.debug(cdlc_file)
        # logger.debug("-----------------------------")

    # TODO refactor this. it should be like
    # - get_requests from RS playlist
    # - get filenames from DB
    # - move files
    def move_requested_cdlcs_to_destination(self):
        playlist = get_playlist(self.phpsessid)

        song_data_set = set()

        for sr in playlist["playlist"]:
            sr_id = sr['id']
            for cdlc in sr["dlc_set"]:
                try:
                    rspl_id = cdlc['id']
                except TypeError:
                    raise RSPlaylistNotLoggedInError

                # Do not load official DLC files
                if cdlc["official"] == 4:
                    continue

                cdlc_id = cdlc["cdlc_id"]
                artist = cdlc["artist"]
                title = cdlc["title"]
                logger.log(str(rspl_id) + " - " + str(cdlc_id) + " - " + artist + " - " + title)

                song_data = SongData(sr_id, cdlc_id)

                with con:
                    rows = self.get_song_from_db(artist, title)

                    if len(rows) <= 0:
                        # remove special chars
                        artist_norm = self.remove_special_chars(artist)
                        title_norm = self.remove_special_chars(title)
                        rows = self.get_song_from_db(artist_norm, title_norm)

                    if len(rows) > 0:
                        logger.debug("---- sr " + str(sr["position"]) + " -------")
                        for element in rows:
                            song_file_name = str(element[0])
                            song_data.song_file_name = song_file_name;
                            logger.debug("row=" + song_file_name)
                            song_data_set.add(song_data)
                    else:
                        logger.debug("User must download the song: cdlc_id={} - {} - {}".format(cdlc_id, artist, title))
                        rs_playlist.set_tag_to_download(self.phpsessid, song_data.sr_id)

                con.commit()

        if len(song_data_set) > 0:
            logger.warning("---- Files to move from archive according to the requests: " + str(song_data_set))
        else:
            logger.warning("---- The playlist is empty, nothing to move!")

        actually_loaded_songs = set()
        for song_data in song_data_set:
            if song_data.song_file_name in self.loaded_songs:
                rs_playlist.set_tag_loaded(self.phpsessid, song_data.sr_id)
            else:
                song_to_move = os.path.join(self.cdlc_archive_dir, song_data.song_file_name)
                moved = file_utils.move_file(song_to_move, self.destination_directory, MODULE_NAME)
                if moved:
                    logger.debug(
                        "The song were moved from the archive to under RS. Moved file: {}".format(song_to_move))
                    self.loaded_songs.add(song_data.song_file_name)
                    actually_loaded_songs.add(song_data.song_file_name)
                    rs_playlist.set_tag_loaded(self.phpsessid, song_data.sr_id)
                else:
                    logger.debug("Could not move file: {}".format(song_to_move))
                    self.missing_songs.add(song_data.song_file_name)
                    rs_playlist.set_tag_to_download(self.phpsessid, song_data.sr_id)

        if len(actually_loaded_songs) > 0:
            logger.warning("---- Files newly moved and will be parsed: " + str(actually_loaded_songs))
        if len(self.missing_songs) > 0:
            logger.error("---- Missing files but found in Database: " + str(self.missing_songs))

    @staticmethod
    def remove_special_chars(text):
        # return unicodedata.normalize('NFD', text).encode('ascii', 'ignore')
        return ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')

    @staticmethod
    def get_song_from_db(artist, title):
        cur = con.cursor()
        execute = cur.execute("SELECT colFileName FROM songs where colArtist like ? and colTitle like ?",
                              ("%" + artist + "%", "%" + title + "%"))
        rows = execute.fetchall()
        return rows
