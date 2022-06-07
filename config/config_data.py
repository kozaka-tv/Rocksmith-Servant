from config.configReader import ConfigReader

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


class ConfigData:
    def __init__(self, conf):
        self.confReader = ConfigReader()

        self.sniffer = ConfRockSniffer(conf)
        self.setlist_logger = ConfSetlistLogger(conf)
        self.file_manager = ConfFileManager(self.confReader)
        # TODO CDLCImporter?
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


class ConfSongLoader:
    def __init__(self, conf):
        self.enabled = conf.get_bool(SECTION_SONG_LOADER, KEY_ENABLED)
        self.twitch_channel = conf.get(SECTION_SONG_LOADER, "twitch_channel")
        self.phpsessid = conf.get(SECTION_SONG_LOADER, "PHPSESSID")
        self.cdlc_dir = conf.get(SECTION_SONG_LOADER, "cdlc_dir")
        self.cfsm_file_name = conf.get(SECTION_SONG_LOADER, "cfsm_file_name")
        self.cdlc_archive_dir = conf.get(SECTION_SONG_LOADER, "cdlc_archive_dir")
        self.destination_directory = conf.get(SECTION_FILE_MANAGER, "destination_directory")
        self.rocksmith_cdlc_dir = conf.get(SECTION_SONG_LOADER, "rocksmith_cdlc_dir")
        self.cdlc_import_json_file = conf.get(SECTION_SONG_LOADER, "cdlc_import_json_file")
        self.allow_load_when_in_game = conf.get_bool(SECTION_SONG_LOADER, "allow_load_when_in_game")


class ConfSceneSwitcher:
    def __init__(self, conf):
        self.enabled = conf.get_bool(SECTION_SCENE_SWITCHER, KEY_ENABLED)


# TODO OBS
# TODO Behaviour

class ConfDebugger:
    def __init__(self, conf):
        self.debug = conf.get_bool(SECTION_DEBUGGING, "debug")
        self.interval = conf.get(SECTION_DEBUGGING, "debug_log_interval", int)
