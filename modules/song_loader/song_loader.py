import json
import os
import pathlib
import urllib.request
from time import sleep

from utils import logger

IMPORT_DIR = 'import'
DEFAULT_CFSM_FILE_NAME = 'SongsMasterGrid.json'


class SongLoader:
    def __init__(self, enabled, allow_load_when_in_game, cfsm_file_name):
        self.enabled = enabled
        self.allow_load_when_in_game = allow_load_when_in_game
        self.cfsm_file_name = cfsm_file_name

        # TODO maybe call this different...do we need this?
        self.raw_playlist = None

        # TODO this should be maybe in run?
        self.create_import_directory()

    # @staticmethod
    def create_import_directory(self):
        if self.enabled:
            logger.warning("Creating import directory to: {}".format(os.path.join(IMPORT_DIR)))
            pathlib.Path(os.path.join(IMPORT_DIR)).mkdir(parents=True, exist_ok=True)

    def load(self):
        if self.enabled:
            # TODO remove this log
            logger.log("Song Loader is running... " + self.cfsm_file_name)
            pass
            # TODO or maybe this should be configurable?
            # else:  # load songs only in case we are not in game to avoid lagging in game
            # self.get_playlist()

    def get_playlist(self):
        # TODO sleep to avoid too much requests
        sleep(5)
        with urllib.request.urlopen("https://rsplaylist.com/ajax/playlist.php?channel=kozaka") as url:
            data = json.loads(url.read().decode())
        self.raw_playlist = data
        logger.warning(data)
