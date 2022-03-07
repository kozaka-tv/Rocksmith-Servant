import os

import requests

from utils.exceptions import ConfigError

# TODO get from the config
CHANNEL = "kozaka"

RS_PLAYLIST_HOME = "https://rsplaylist.com/ajax"
URL_PLAYLIST = RS_PLAYLIST_HOME + "/playlist.php?channel=%s"
URL_REQUESTS = RS_PLAYLIST_HOME + "/requests.php?channel=%s"
URL_TAG_SET = URL_REQUESTS + "&action=set-tag&id=%s&tag=%s&value=true"
URL_TAG_UNSET = URL_REQUESTS + "&action=set-tag&id=%s&tag=%s&value=false"
# https://rsplaylist.com/ajax/requests.php?channel=kozaka&action=set-tag&id=1305252&tag=8c8c2924&value=true
# https://rsplaylist.com/ajax/requests.php?channel=kozaka&action=set-tag&id=1305252&tag=8c8c2924&value=false

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
    return requests.get(URL_PLAYLIST % CHANNEL, cookies={'PHPSESSID': phpsessid}).json()


def tag_set(phpsessid):
    url = URL_TAG_SET % (CHANNEL, "1305252", "8c8c2924")
    cookies = {'PHPSESSID': phpsessid}
    playlist = requests.get(url, cookies=cookies).json()
    return playlist
