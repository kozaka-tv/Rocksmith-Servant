import os

from config.configReader import ConfigReader
from utils import rs_playlist
from utils.exceptions import ConfigError

SECTION_ROCK_SNIFFER = "RockSniffer"
SECTION_SETLIST_LOGGER = "SetlistLogger"
SECTION_CDLC_IMPORTER = "CDLCImporter"
SECTION_SONG_LOADER = "SongLoader"
SECTION_SCENE_SWITCHER = "SceneSwitcher"
SECTION_FILE_MANAGER = "FileManager"
# OBS
# Behaviour
SECTION_DEBUGGING = "Debugging"

# Key name definitions
KEY_ENABLED = "enabled"

TAG_TO_DOWNLOAD = "rspl_tag_to_download"
TAG_DOWNLOADED = "rspl_tag_downloaded"
TAG_LOADED = "rspl_tag_loaded"
TAG_NEW_VIEWER_REQ = "rspl_tag_new_viewer_request"
TAG_RAIDER_REQ = "rspl_tag_raider_request"
TAG_VIP_VIEWER_REQ = "rspl_tag_vip_viewer_request"

NL = os.linesep
ERR_MSG_PHPSESSID = "You have not logged in to RSPlaylist, or your PHP Session ID (phpsessid) is wrong." + NL + \
                    "Please login to RSPlaylist and try to start again!" + NL + \
                    "If you still get this error message, check you PHP Session ID in your config.ini!" + NL + \
                    "You may enter more than one ID, separated by ';'" + NL + \
                    "The PHPSESSID is needed to get data from your RS Playlist request page." + NL + \
                    "You can have the PHPSESSID from the cookie of your browser " \
                    "after you logged in into the RS Playlist page." + NL + \
                    "Optionally, use the Tampermonkey script, what could be found under /misc/tampermonkey " + NL + \
                    "with the name: 'RS Playlist enhancer and simplifier.user.js'" + NL + \
                    "or install it from https://greasyfork.org/en/scripts/440738-rs-playlist-enhancer-and-simplifier"
ERR_MSG_CDLC_IMPORTER = "Please set your directory and file name where the json file is located " + NL + \
                        "what contains all the CDLC information (exported from CFSM) what " + NL + \
                        "the Servant have to import into the database!"
ERR_MSG_RSPL_TAG = "Missing or undefined tag value of the tag '{}' in the config!" + NL + \
                   "Please create a tag in RS Playlist and enter the value into the config!" + NL + \
                   "BAD: {}={}"


class ConfigData:
    def __init__(self, conf):
        self.confReader = ConfigReader()

        self.sniffer = ConfRockSniffer(conf)
        self.setlist_logger = ConfSetlistLogger(conf)
        self.file_manager = ConfFileManager(self.confReader)
        self.cdlc_importer = ConfCDLCImporter(conf)
        self.song_loader = ConfSongLoader(conf)
        self.scene_switcher = ConfSceneSwitcher(conf)
        self.debugger = ConfDebugger(conf)


class ConfRockSniffer:
    def __init__(self, conf):
        self.enabled = conf.get_bool(SECTION_ROCK_SNIFFER, KEY_ENABLED)
        self.host = conf.get(SECTION_ROCK_SNIFFER, "host")
        self.port = conf.get(SECTION_ROCK_SNIFFER, "port")


class ConfSetlistLogger:
    def __init__(self, conf):
        self.enabled = conf.get_bool(SECTION_SETLIST_LOGGER, KEY_ENABLED)
        self.setlist_path = conf.get(SECTION_SETLIST_LOGGER, "setlist_path")


class ConfFileManager:
    def __init__(self, conf):
        self.enabled = conf.get_bool(SECTION_FILE_MANAGER, KEY_ENABLED)
        self.source_directories = conf.get_set(SECTION_FILE_MANAGER, "source_directories")
        self.destination_directory = conf.get(SECTION_FILE_MANAGER, "destination_directory")
        self.using_cfsm = conf.get(SECTION_FILE_MANAGER, "using_cfsm")


class ConfCDLCImporter:
    def __init__(self, conf):
        self.enabled = conf.get_bool(SECTION_CDLC_IMPORTER, KEY_ENABLED)
        self.cdlc_import_json_file = validate_and_get_cdlc_import_json_file(
            conf.get(SECTION_CDLC_IMPORTER, "cdlc_import_json_file"))


class ConfSongLoader:
    def __init__(self, conf):
        self.enabled = conf.get_bool(SECTION_SONG_LOADER, KEY_ENABLED)
        if self.enabled:
            self.twitch_channel = conf.get(SECTION_SONG_LOADER, "twitch_channel")
            self.phpsessid = validate_and_get_phpsessid(conf, self.twitch_channel)
            self.cdlc_dir = conf.get(SECTION_SONG_LOADER, "cdlc_dir")
            self.rspl_tags = RSPLTags(conf)
            self.cfsm_file_name = conf.get(SECTION_SONG_LOADER, "cfsm_file_name")
            self.cdlc_archive_dir = conf.get(SECTION_SONG_LOADER, "cdlc_archive_dir")
            self.destination_directory = conf.get(SECTION_FILE_MANAGER, "destination_directory")
            self.rocksmith_cdlc_dir = conf.get(SECTION_SONG_LOADER, "rocksmith_cdlc_dir")
            self.cdlc_import_json_file = conf.get(SECTION_SONG_LOADER, "cdlc_import_json_file")
            self.allow_load_when_in_game = conf.get_bool(SECTION_SONG_LOADER, "allow_load_when_in_game")


class RSPLTags:
    def __init__(self, conf):
        self.tag_to_download = get_tag_validated(conf, TAG_TO_DOWNLOAD)
        self.tag_downloaded = get_tag(conf, TAG_DOWNLOADED)
        self.tag_loaded = get_tag_validated(conf, TAG_LOADED)
        self.tag_new_viewer_request = get_tag(conf, TAG_NEW_VIEWER_REQ)
        self.tag_raider_request = get_tag(conf, TAG_RAIDER_REQ)
        self.tag_vip_viewer_request = get_tag(conf, TAG_VIP_VIEWER_REQ)


class ConfSceneSwitcher:
    def __init__(self, conf):
        self.enabled = conf.get_bool(SECTION_SCENE_SWITCHER, KEY_ENABLED)


# TODO OBS
# TODO Behaviour

class ConfDebugger:
    def __init__(self, conf):
        self.debug = conf.get_bool(SECTION_DEBUGGING, "debug")
        self.interval = conf.get(SECTION_DEBUGGING, "debug_log_interval", int)


def validate_and_get_phpsessid(conf, twitch_channel):
    phpsessid = conf.get(SECTION_SONG_LOADER, "phpsessid")
    if phpsessid is None or phpsessid.startswith('<Enter your'):
        raise ConfigError(ERR_MSG_PHPSESSID)

    phpsessid_set = conf.get_set(SECTION_SONG_LOADER, "phpsessid")

    for phpsessid in phpsessid_set:
        viewers = rs_playlist.get_viewers(twitch_channel, phpsessid)
        if viewers.get("result") != "Error":
            return phpsessid

    raise ConfigError(ERR_MSG_PHPSESSID)


def validate_and_get_cdlc_import_json_file(cdlc_import_json_file):
    if cdlc_import_json_file is None or cdlc_import_json_file.startswith('<Enter your'):
        raise ConfigError(ERR_MSG_CDLC_IMPORTER)
    return cdlc_import_json_file


def get_tag(conf, tag_name):
    value = conf.get(SECTION_SONG_LOADER, tag_name)
    if value is None or value.startswith('<Create a tag in RS Playlist'):
        return None
    return value


def get_tag_validated(conf, tag_name):
    value = conf.get(SECTION_SONG_LOADER, tag_name)
    if value is None or value.startswith('<Create a tag in RS Playlist'):
        raise ConfigError(ERR_MSG_RSPL_TAG.format(tag_name, tag_name, value))
    return value
