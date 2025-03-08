import logging
import pprint
from typing import Dict

from modules.servant.song_loader.dataclasses.rs_playlist_data import ChannelTag
from utils.exceptions import TagConfigError

log = logging.getLogger()

USER_TAGS_MESSAGE = "Tags set by the user in RSPlaylist"
SYSTEM_TAGS_MESSAGE = "System tags set in RSPlaylist"


def validate_and_log_rspl_tags(channel_tags: Dict[str, ChannelTag], rspl_tags) -> None:
    """
    Validates RSPlaylist tags and logs user/system tags.
    """
    # Separate tags into user and system categories
    user_tags = __filter_tags(channel_tags, is_user=True)
    system_tags = __filter_tags(channel_tags, is_user=False)

    # Log the tags
    __log_tags(user_tags, log.warning, USER_TAGS_MESSAGE)
    __log_tags(system_tags, log.info, SYSTEM_TAGS_MESSAGE)

    # Validate critical user tags
    __validate_required_user_tags(rspl_tags, user_tags)


def __validate_required_user_tags(rspl_tags, user_tags: Dict[str, str]) -> None:
    """
    Validates that required user tags exist in the set of user-provided tags.
    """
    user_tags_set = set(user_tags.values())
    required_tags = {
        rspl_tags.tag_to_download: "tag_to_download",
        rspl_tags.tag_loaded: "tag_loaded",
    }

    for tag, tag_name in required_tags.items():
        try:
            user_tags_set.remove(tag)
        except KeyError as exc:
            raise TagConfigError(tag_name, tag, required_tags, user_tags) from exc


def __filter_tags(tags_to_filter, is_user):
    return {value.name: key for key, value in tags_to_filter.items() if value.user == is_user}


def __log_tags(tags_to_log, log_function, prefix_message):
    formatted_tags = pprint.pformat(tags_to_log)
    log_function(f"{prefix_message}:\n{formatted_tags}")
