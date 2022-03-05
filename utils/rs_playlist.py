import os

import requests

from utils.exceptions import ConfigError

NL = os.linesep
ERR_MSG_PHPSESSID = "Please set your PHP Session ID into the config!" + NL + \
                    "The PHPSESSID is needed to get data from your RS Playlist request page." + NL + \
                    "You can have the PHPSESSID from the cookie of your browser " \
                    "after you logged in into the RS Playlist page." + NL + \
                    "Optionally, use the Tampermonkey script, what could be found under /misc/tampermonkey " \
                    "with the name: 'RS Playlist enhancer and simplifier.user.js'" + NL + \
                    "or install it from https://greasyfork.org/en/scripts/440738-rs-playlist-enhancer-and-simplifier"


def check_phpsessid(phpsessid):
    if phpsessid is None or phpsessid.startswith('<Enter your'):
        raise ConfigError(ERR_MSG_PHPSESSID)
    return phpsessid


def get_playlist(phpsessid):
    rs_playlist_url = "https://rsplaylist.com/ajax/playlist.php?channel=kozaka"
    cookies = {'PHPSESSID': phpsessid}
    playlist = requests.get(rs_playlist_url, cookies=cookies).json()
    return playlist
