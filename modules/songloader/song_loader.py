import json
import urllib.request
from time import sleep

import logger


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
        self.get_playlist()

    def get_playlist(self):
        # TODO sleep to avoid too much requests
        sleep(5)
        with urllib.request.urlopen("https://rsplaylist.com/ajax/playlist.php?channel=kozaka") as url:
            data = json.loads(url.read().decode())
        self.raw_playlist = data
        logger.notice(data)
