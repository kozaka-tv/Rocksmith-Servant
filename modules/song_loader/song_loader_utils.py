import logging

from deepdiff import DeepDiff

log = logging.getLogger()


def playlist_does_not_changed(old_playlist, new_playlist):
    diff = DeepDiff(old_playlist, new_playlist, exclude_regex_paths="\\['inactive_time'\\]")
    if str(diff) == "{}":
        log.debug("Playlist does not changed!")
        return True

    log.debug("Playlist has been changed! Diffs: %s", diff)
    return False


def log_loaded_cdlc_files(cdlc_files):
    if len(cdlc_files) > 0:
        log.info('Found %s into Rocksmith loaded CDLC files.', len(cdlc_files))

        if log.isEnabledFor(logging.DEBUG):
            log.debug("---------- Found %s files already loaded into Rocksmith:", len(cdlc_files))
            for cdlc_file in cdlc_files:
                log.debug(cdlc_file)
            log.debug("-----------------------------")
