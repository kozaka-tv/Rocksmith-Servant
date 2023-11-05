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
