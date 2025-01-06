import logging
import pprint

log = logging.getLogger()


def log_available_rspl_tags(tags):
    def _filter_tags(tags_to_filter, is_user):
        return {value.name: key for key, value in tags_to_filter.items() if value.user == is_user}

    def _log_tags(tags_to_log, log_function, prefix_message):
        formatted_tags = pprint.pformat(tags_to_log)
        log_function(f"{prefix_message}:\n{formatted_tags}")

    # tags = self.rsplaylist.channel_tags
    user_tags = _filter_tags(tags, is_user=True)
    system_tags = _filter_tags(tags, is_user=False)

    _log_tags(user_tags, log.warning, "Tags set by the user in RSPlaylist")
    _log_tags(system_tags, log.info, "System tags set in RSPlaylist")
