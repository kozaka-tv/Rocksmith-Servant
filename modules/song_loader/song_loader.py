import os
import pathlib
import sqlite3
from time import sleep

import requests

from utils import logger, file_utils

MODULE_NAME = "SongLoader"
CDLC_DIR = '../../import'
DEFAULT_CFSM_FILE_NAME = '../../temp/temp_song_loader/SongsMasterGrid.json'

con = sqlite3.connect('./servant.db')


class SongLoader:
    def __init__(self, enabled, cdlc_dir='import', cfsm_file_name=DEFAULT_CFSM_FILE_NAME,
                 allow_load_when_in_game=True):
        self.enabled = enabled
        self.cdlc_dir = os.path.join(cdlc_dir)
        self.cfsm_file_name = cfsm_file_name
        self.songs_to_load = os.path.join(cdlc_dir, cfsm_file_name)
        self.allow_load_when_in_game = allow_load_when_in_game

        self.first_run = True

        # TODO maybe call this different...do we need this?
        self.raw_playlist = None

        # TODO this should be maybe in run or in config reader?
        self.create_cdlc_directory()

    # @staticmethod
    def create_cdlc_directory(self):
        if self.enabled:
            # self.cdlc_dir = os.path.join(CDLC_DIR)
            logger.warning("Creating cdlc directory to: {}".format(self.cdlc_dir))
            pathlib.Path(self.cdlc_dir).mkdir(parents=True, exist_ok=True)

    def load(self):
        if self.enabled:
            # TODO remove this log
            logger.warning("---------------------- ")
            logger.warning("Song Loader is running... ")

            if self.first_run:
                logger.log("Try to load new songs for the CFSM file: {}".format(self.songs_to_load))
                self.first_run = False

            self.get_file_to_import()

            # pass
            # TODO or maybe this should be configurable?
            # else:  # load songs only in case we are not in game to avoid lagging in game
            self.get_playlist()

            # TODO remove this sleep
            sleep(3)

    def get_file_to_import(self):
        path = file_utils.get_file_path(self.cdlc_dir, self.cfsm_file_name)
        logger.log('CFSM_file to load: {}'.format(path), MODULE_NAME)

    def get_playlist(self):
        # TODO sleep to avoid too much requests
        # sleep(3)

        rs_playlist_url = "https://rsplaylist.com/ajax/playlist.php?channel=kozaka"
        # TODO get the PHPSESSID from config!
        cookies = {'PHPSESSID': '4hsjtoq26pvtavh062jdsplfp8'}

        playlist = requests.get(rs_playlist_url, cookies=cookies).json()
        # logger.log(playlist)

        for sr in playlist["playlist"]:
            for cdlc in sr["dlc_set"]:
                id_ = cdlc["id"]
                cdlc_id = cdlc["cdlc_id"]
                artist = cdlc["artist"]
                title = cdlc["title"]
                # logger.log(str(id_) + " - " + str(cdlc_id) + " - " + artist + " - " + title)

                with con:
                    cur = con.cursor()
                    execute = cur.execute("SELECT colFileName FROM songs where colArtist like ? and colTitle like ?",
                                          ("%" + artist + "%", "%" + title + "%"))

                    rows = execute.fetchall()

                    if len(rows) > 0:
                        logger.log("---- sr " + str(sr["position"]) + " -------")
                        for element in rows:
                            logger.debug("rows" + str(element))

                    con.commit()
