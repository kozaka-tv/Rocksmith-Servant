import os
import sys

from config.config_data import ConfigData, ConfRockSniffer, ConfSetlistLogger, ConfSceneSwitcher, ConfSongLoader, \
    ConfFileManager, RSPLTagNames
from config.config_reader import log, ConfigReader
from utils import string_utils
from utils.exceptions import ConfigError
from utils.rs_playlist_util import get_viewers

SECTION_ROCK_SNIFFER = "RockSniffer"
SECTION_SETLIST_LOGGER = "SetlistLogger"
SECTION_SONG_LOADER = "SongLoader"
SECTION_SCENE_SWITCHER = "SceneSwitcher"
SECTION_FILE_MANAGER = "FileManager"

# Key name definitions
KEY_ENABLED = "enabled"

TAG_TO_DOWNLOAD = "rspl_tag_to_download"
TAG_DOWNLOADED = "rspl_tag_downloaded"
TAG_LOADED = "rspl_tag_loaded"
TAG_NEW_VIEWER_REQ = "rspl_tag_new_viewer_request"
TAG_RAIDER_REQ = "rspl_tag_raider_request"
TAG_VIP_VIEWER_REQ = "rspl_tag_vip_viewer_request"

NL = os.linesep
PHPSESSID_INFO = "The PHPSESSID is needed to get data from your RS Playlist request page." + NL + \
                 ("You can have the PHPSESSID from the cookie of your browser after you logged in into the RS Playlist "
                  "page.") + NL + \
                 "Optionally, use the Tampermonkey script, what could be found under /misc/tampermonkey " + NL + \
                 "with the name: 'RS Playlist enhancer and simplifier.user.js'" + NL + \
                 "or install it from https://greasyfork.org/en/scripts/440738-rs-playlist-enhancer-and-simplifier"
ERR_MSG_PHPSESSID_MISSING = f"Your PHP Session ID (phpsessid) is missing from the config.ini!{NL}{PHPSESSID_INFO}"
ERR_MSG_PHPSESSID = "Eiter, you are not logged in, into the RSPlaylist, " + \
                    "or your PHP Session ID (phpsessid) is wrong, " + \
                    "or RSPlaylist ist not enabled on your Channel Settings." + NL + \
                    ("Please login to RSPlaylist, check your RSPL and Servant configuration "
                     "and try to start again!") + NL + \
                    "If you still get this error message, check you PHP Session ID in your config.ini!" + NL + \
                    "You may enter more than one ID, separated by ';'" + NL + \
                    PHPSESSID_INFO
ERR_MSG_RSPL_TAG = "Missing or undefined tag value of the tag '{}' in the config!" + NL + \
                   "Please create a tag in RS Playlist and enter the value into the config!" + NL + \
                   "BAD: {}={}"


def load_config(config_file_path: str) -> ConfigData:
    conf = ConfigReader(config_file_path)

    try:
        conf_rocksniffer = __create_conf_rocksniffer(conf)
        conf_setlist_logger = __create_conf_setlist_logger(conf)
        conf_file_manager = __create_conf_file_manager(conf)
        conf_song_loader = __create_conf_song_loader(conf)
        conf_scene_switcher = __create_conf_scene_switcher(conf)

        config_data = ConfigData(conf_rocksniffer,
                                 conf_setlist_logger,
                                 conf_file_manager,
                                 conf_song_loader,
                                 conf_scene_switcher)

    except ConfigError as e:
        log.error(e)
        sys.exit(1)

    return config_data


def __create_conf_rocksniffer(conf: ConfigReader) -> ConfRockSniffer:
    enabled = conf.get_bool(SECTION_ROCK_SNIFFER, KEY_ENABLED)
    host = conf.get(SECTION_ROCK_SNIFFER, "host")
    port = conf.get(SECTION_ROCK_SNIFFER, "port")

    return ConfRockSniffer(enabled, host, port)


def __create_conf_setlist_logger(conf):
    enabled = conf.get_bool(SECTION_SETLIST_LOGGER, KEY_ENABLED)
    setlist_path = conf.get(SECTION_SETLIST_LOGGER, "setlist_path")
    return ConfSetlistLogger(enabled, setlist_path)


def __create_conf_file_manager(conf):
    enabled = conf.get_bool(SECTION_FILE_MANAGER, KEY_ENABLED)
    destination_dir = conf.get(SECTION_FILE_MANAGER, "destination_dir")
    using_cfsm = conf.get(SECTION_FILE_MANAGER, "using_cfsm")
    download_dirs = conf.get_set(SECTION_FILE_MANAGER, "download_dirs")
    return ConfFileManager(enabled, destination_dir, using_cfsm, download_dirs)


# Define constants for tag names
TAG_NAMES = [
    TAG_TO_DOWNLOAD,
    TAG_DOWNLOADED,
    TAG_LOADED,
    TAG_NEW_VIEWER_REQ,
    TAG_RAIDER_REQ,
    TAG_VIP_VIEWER_REQ
]


def __create_rspl_tags(conf):
    tags = __fetch_tags(conf, TAG_NAMES)
    return RSPLTagNames(*tags)


def __fetch_tags(conf, tag_names):
    """
    Fetch multiple tags based on the provided tag names.
    """
    return [__get_tag(conf, tag_name) for tag_name in tag_names]


def __create_conf_song_loader(conf):
    enabled = conf.get_bool(SECTION_SONG_LOADER, KEY_ENABLED)
    twitch_channel = conf.get(SECTION_SONG_LOADER, "twitch_channel")
    phpsessid = __validate_and_get_phpsessid(conf, twitch_channel)
    rspl_tags = __create_rspl_tags(conf)
    cdlc_archive_dir = conf.get(SECTION_SONG_LOADER, "cdlc_archive_dir")
    destination_dir = conf.get(SECTION_FILE_MANAGER, "destination_dir")
    rocksmith_cdlc_dir = conf.get(SECTION_SONG_LOADER, "rocksmith_cdlc_dir")
    allow_load_when_in_game = conf.get_bool(SECTION_SONG_LOADER, "allow_load_when_in_game")
    return ConfSongLoader(enabled,
                          twitch_channel,
                          phpsessid,
                          rspl_tags,
                          cdlc_archive_dir,
                          destination_dir,
                          rocksmith_cdlc_dir,
                          allow_load_when_in_game)


def __create_conf_scene_switcher(conf):
    enabled = conf.get_bool(SECTION_SCENE_SWITCHER, KEY_ENABLED)
    return ConfSceneSwitcher(enabled)


def __validate_and_get_phpsessid(conf, twitch_channel):
    phpsessid = conf.get(SECTION_SONG_LOADER, "phpsessid")
    if string_utils.is_blank(phpsessid) or phpsessid.startswith('<Enter your'):
        raise ConfigError(ERR_MSG_PHPSESSID_MISSING)

    phpsessid_set = conf.get_set(SECTION_SONG_LOADER, "phpsessid")

    for phpsessid in phpsessid_set:
        viewers = get_viewers(twitch_channel, phpsessid)
        if viewers.get("result") != "Error":
            return phpsessid

    raise ConfigError(ERR_MSG_PHPSESSID)


def __get_tag(conf, tag_name):
    value = conf.get(SECTION_SONG_LOADER, tag_name)
    if not value or value.startswith('<Create a tag in RS Playlist'):
        return None
    return value


def __get_tag_validated(conf, tag_name):
    value = conf.get(SECTION_SONG_LOADER, tag_name)
    if not value or value.startswith('<Create a tag in RS Playlist'):
        raise ConfigError(ERR_MSG_RSPL_TAG.format(tag_name, tag_name, value))
    return value
