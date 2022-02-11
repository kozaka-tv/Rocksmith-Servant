import json
import os
import pathlib
import urllib.request
from time import sleep

from utils import logger, file_utils

MODULE_NAME = "SongLoader"
CDLC_DIR = 'import'
DEFAULT_CFSM_FILE_NAME = 'SongsMasterGrid.json'


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
            # TODO remove this log + sleep
            logger.log("Song Loader is running... ")

            if self.first_run:
                logger.log("Try to load new songs for the CFSM file: {}".format(self.songs_to_load))
                self.first_run = False

            self.get_files_to_import()

            # pass
            # TODO or maybe this should be configurable?
            # else:  # load songs only in case we are not in game to avoid lagging in game
            self.get_playlist()

            # TODO remove this sleep
            sleep(5)

    def get_files_to_import(self):
        path = file_utils.get_file_path(self.cdlc_dir, self.cfsm_file_name)
        logger.log('CFSM_file to load: {}'.format(path), MODULE_NAME)

    def get_playlist(self):
        # TODO sleep to avoid too much requests
        with urllib.request.urlopen("https://rsplaylist.com/ajax/playlist.php?channel=kozaka") as url:
            data = json.loads(url.read().decode())
        self.raw_playlist = data
        logger.warning(data)
