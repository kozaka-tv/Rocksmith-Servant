import os

SNIFFER_ERROR_MSG = "--- Could not connect to Rocksniffer!" + os.linesep + \
                    "--------------------------------------------------" + os.linesep + \
                    "Please check that is Rocksniffer running or not!" + os.linesep + \
                    "Please check host and port defined in config:" + os.linesep + \
                    "host={}" + os.linesep + \
                    "port={}" + os.linesep + \
                    "--------------------------------------------------"

RSPL_LOGIN_ERROR_MSG = "--- PHPSESSID in from the cookies in the config is not valid anymore!" + os.linesep + \
                       "--------------------------------------------------" + os.linesep + \
                       "Please login on RS Playlist page and get the PHPSESSID from the cookies!" + os.linesep + \
                       "Then add/change it in the config and restart Servant if needed!" + os.linesep + \
                       "--------------------------------------------------"


class ConfigError(Exception):
    def __init__(self, error_msg):
        super().__init__(error_msg)


class SongLoaderError(Exception):
    def __init__(self, error_msg):
        super().__init__(error_msg)


class RocksnifferConnectionError(Exception):
    def __init__(self, host, port):
        super().__init__(SNIFFER_ERROR_MSG.format(host, port))


class RSPlaylistNotLoggedInError(Exception):
    def __init__(self):
        super().__init__(RSPL_LOGIN_ERROR_MSG)
