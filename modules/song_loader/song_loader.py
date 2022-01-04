import json
import urllib.request
from time import sleep

from utils import logger


class SongLoader:
    def __init__(self, enabled):
        """
        Song Loader
        :param enabled: Is the Module enabled?
        """
        self.enabled = enabled
        # TODO maybe call this different...do we need this?
        self.raw_playlist = None
        pass

    def load(self):
        if self.enabled:
            # TODO or maybe this should be configurable?
            # else:  # load songs only in case we are not in game to avoid lagg in game
            self.get_playlist()

    def get_playlist(self):
        # TODO sleep to avoid too much requests
        sleep(5)
        with urllib.request.urlopen("https://rsplaylist.com/ajax/playlist.php?channel=kozaka") as url:
            data = json.loads(url.read().decode())
        self.raw_playlist = data
        logger.notice(data)
