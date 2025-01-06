import logging
import pprint
from typing import Dict

from modules.servant.song_loader.rs_playlist_data import ChannelTag

log = logging.getLogger()


def log_available_rspl_tags(rsplaylist_channel_tags: Dict[str, ChannelTag]) -> None:
    user_tags = __filter_tags(rsplaylist_channel_tags, is_user=True)
    system_tags = __filter_tags(rsplaylist_channel_tags, is_user=False)

    __log_tags(user_tags, log.warning, "Tags set by the user in RSPlaylist")
    __log_tags(system_tags, log.info, "System tags set in RSPlaylist")


def __filter_tags(tags_to_filter, is_user):
    return {value.name: key for key, value in tags_to_filter.items() if value.user == is_user}


def __log_tags(tags_to_log, log_function, prefix_message):
    formatted_tags = pprint.pformat(tags_to_log)
    log_function(f"{prefix_message}:\n{formatted_tags}")
