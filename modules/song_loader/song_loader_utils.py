import logging
import os

from deepdiff import DeepDiff

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


# TODO this could be a more generic, song list logger!
def log_loaded_cdlc_files(cdlc_files):
    if len(cdlc_files) > 0:
        log.info('Found %s into Rocksmith loaded CDLC files.', len(cdlc_files))

        if log.isEnabledFor(logging.DEBUG):
            log.debug("---------- Found %s files already loaded into Rocksmith:", len(cdlc_files))
            for cdlc_file in cdlc_files:
                log.debug(cdlc_file)
            log.debug("-----------------------------")


def update_tags(song_data, sr):
    song_data.tags.clear()
    for tag in sr['tags']:
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
