import os

NL = os.linesep

SNIFFER_ERR_MSG = "--- Could not connect to Rocksniffer!" + NL + \
                  "--------------------------------------------------" + NL + \
                  "Please check that is Rocksniffer running or not!" + NL + \
                  "Please check host and port defined in config:" + NL + \
                  "host={}" + NL + \
                  "port={}" + NL + \
                  "--------------------------------------------------"

RSPL_LOGIN_ERR_MSG = "--- PHPSESSID in from the cookies in the config is not valid anymore!" + NL + \
                     "--------------------------------------------------" + NL + \
                     "Please login on RS Playlist page and get the PHPSESSID from the cookies!" + NL + \
                     "Then add/change it in the config and restart Servant if needed!" + NL + \
                     "" + NL + \
                     "Or optionally, use the Tampermonkey script, what could be found under /misc/tampermonkey " \
                     "with the name: 'RS Playlist enhancer and simplifier.user.js'" + NL + \
                     "or install it from " \
                     "https://greasyfork.org/en/scripts/440738-rs-playlist-enhancer-and-simplifier" + NL + \
                     "--------------------------------------------------"

RSPL_PLAYLIST_NOT_ENABLED_ERR_MSG = ("Your playlist is not found on RSPL page. Probably the playlist is not enabled "
                                     "on your channel! Go onto RSPL page, General Settings and click "
                                     "'Enable the playlist on your channel'")


class ConfigError(Exception):
    def __init__(self, error_msg):
        super().__init__(error_msg)


class SongLoaderError(Exception):
    def __init__(self, error_msg):
        super().__init__(error_msg)


class RocksnifferConnectionError(Exception):
    def __init__(self, host, port):
        super().__init__(SNIFFER_ERR_MSG.format(host, port))


class RSPLNotLoggedInError(Exception):
    def __init__(self):
        super().__init__(RSPL_LOGIN_ERR_MSG)


class RSPLPlaylistIsNotEnabledError(Exception):
    def __init__(self):
        super().__init__(RSPL_PLAYLIST_NOT_ENABLED_ERR_MSG)


class BadDirectoryError(Exception):
    def __init__(self, error_msg, directory):
        super().__init__(error_msg)
        self.directory = directory

class ExtractError(Exception):
    def __init__(self, error_msg):
        super().__init__(error_msg)

class ExtractError(Exception):
    def __init__(self, error_msg):
        super().__init__(error_msg)
