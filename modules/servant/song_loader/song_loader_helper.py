import logging
import os

from deepdiff import DeepDiff

from common.definitions import KEY_VALUES_OF_AN_OFFICIAL_CDLC
from utils import collection_utils
from utils.exceptions import ConfigError

ENTER_YOUR = '<Enter your'

NL = os.linesep
ERR_MSG_CDLC_ARCHIVE_DIR = "Please set your CDLC archive directory in the config!" + NL + \
                           "This is the directory, where you normally store all of your downloaded CDLC files."

ERR_MSG_ROCKSMITH_CDLC_DIR = "Please set your Rocksmith CDLC directory!" + NL + \
                             "This is the directory, where you normally store all of your CDLC files what you play" \
                             "in the game."

log = logging.getLogger()


def playlist_does_not_changed(old_playlist, new_playlist):
    diff = DeepDiff(old_playlist, new_playlist, exclude_regex_paths="\\['inactive_time'\\]")
    if str(diff) == "{}":
        log.debug("Playlist does not changed!")
        return True

    log.debug("Playlist has been changed! Diffs: %s", diff)
    return False


def update_tags_in_song_data(song_data, playlist_item):
    song_data.tags.clear()
    for tag in playlist_item.tags:
        song_data.tags.add(tag)


def check_cdlc_archive_dir(dir_to_check):
    check_dir(dir_to_check, ERR_MSG_CDLC_ARCHIVE_DIR)
    return os.path.join(dir_to_check)


def check_rocksmith_cdlc_dir(dir_to_check):
    check_dir(dir_to_check, ERR_MSG_ROCKSMITH_CDLC_DIR)
    return os.path.join(dir_to_check)


def check_dir(dir_to_check, error_msg):
    if dir_to_check is None or dir_to_check.startswith(ENTER_YOUR):
        raise ConfigError(error_msg)


def is_official(rspl_official):
    return rspl_official in KEY_VALUES_OF_AN_OFFICIAL_CDLC


def log_new_songs_found(new_songs):
    if new_songs:
        if len(new_songs) > 20:
            log.info("%s new files found", len(new_songs))
        else:
            log.info("%s new files found! Files: %s", len(new_songs), collection_utils.repr_in_multi_line(new_songs))
