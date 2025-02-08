import os

NL = os.linesep

# Error message constants
SNIFFER_ERROR_TEMPLATE = (
        "--- Could not connect to Rocksniffer!" + NL +
        "--------------------------------------------------" + NL +
        "Please check that is Rocksniffer running or not!" + NL +
        "Please check host and port defined in config:" + NL +
        "host={}" + NL +
        "port={}" + NL +
        "--------------------------------------------------"
)

RSPL_LOGIN_ERROR = (
        "--- PHPSESSID in from the cookies in the config is not valid anymore!" + NL +
        "--------------------------------------------------" + NL +
        "Please login on RS Playlist page and get the PHPSESSID from the cookies!" + NL +
        "Then add/change it in the config and restart Servant if needed!" + NL +
        "" + NL +
        "Or optionally, use the Tampermonkey script, which can be found under /misc/tampermonkey " +
        "with the name: 'RS Playlist enhancer and simplifier.user.js'" + NL +
        "or install it from " +
        "https://greasyfork.org/en/scripts/440738-rs-playlist-enhancer-and-simplifier" + NL +
        "--------------------------------------------------"
)

RSPL_PLAYLIST_NOT_ENABLED_ERROR = (
    "Your playlist is not found on RSPL page. Probably the playlist is not enabled "
    "on your channel! Go onto RSPL page, General Settings and click "
    "'Enable the playlist on your channel'"
)


# Base exception class for custom errors
class CheckedException(Exception):
    def __init__(self, error_msg, **kwargs):
        super().__init__(error_msg.format(**kwargs))
        self.details = kwargs


# Custom exception classes
class ConfigError(CheckedException):
    def __init__(self, error_msg, **kwargs):
        super().__init__(error_msg.format(**kwargs))
        self.details = kwargs


class TagConfigError(Exception):
    """
    Custom exception to handle errors related to missing or misconfigured RSPlaylist tags.
    This exception only displays the error message without a traceback.
    """

    def __init__(self, tag_name: str, tag: str, required_tags: dict, user_tags: dict):
        """
        Initializes the TagConfigError.

        :param tag_name: Name of the tag (e.g., 'tag_to_download', 'tag_downloaded').
        :param tag: The missing tag value (what's expected but not present).
        :param required_tags: Dictionary of all required tags with their names.
        :param user_tags: Dictionary of the user-provided tags.
        """
        self.tag_name = tag_name
        self.tag = tag
        self.required_tags = required_tags
        self.user_tags = user_tags
        # Set a detailed error message
        self.message = (
                NL +
                "--- Bad configuration of the tags!" + NL +
                "--------------------------------------------------" + NL +
                "Please check tag definitions in config:" + NL +
                f"Missing or misconfigured required tag: '{tag_name}' with value set in config: '{tag}'" + NL +
                f"Required tags: {required_tags}" + NL +
                f"Tags set in RSPlaylist: {user_tags}" + NL +
                "Please correct the required tags in config according to your tags set in RSPlaylist!" + NL +
                "--------------------------------------------------"
        )
        super().__init__(self.message)


class SongLoaderError(CheckedException):
    def __init__(self, error_msg, **kwargs):
        super().__init__(error_msg.format(**kwargs))


class RocksnifferConnectionError(CheckedException):
    def __init__(self, host, port):
        super().__init__(SNIFFER_ERROR_TEMPLATE, host=host, port=port)


class RSPLNotLoggedInError(CheckedException):
    def __init__(self):
        super().__init__(RSPL_LOGIN_ERROR)


class RSPLPlaylistIsNotEnabledError(CheckedException):
    def __init__(self):
        super().__init__(RSPL_PLAYLIST_NOT_ENABLED_ERROR)


class BadDirectoryError(CheckedException):
    def __init__(self, error_msg, directory):
        super().__init__(error_msg)
        self.directory = directory


class PsarcReaderExtractError(CheckedException):
    def __init__(self, error_msg, **kwargs):
        super().__init__(error_msg.format(**kwargs))
        self.details = kwargs
