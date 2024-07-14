from dataclasses import dataclass, field


@dataclass
class ConfRockSniffer:
    enabled: bool
    host: str
    port: str


@dataclass
class ConfSetlistLogger:
    enabled: bool
    setlist_path: str


@dataclass
class ConfFileManager:
    enabled: bool
    destination_dir: str
    using_cfsm: bool
    download_dirs: set[str] = field(default_factory=set)


@dataclass
class RSPLTags:
    tag_to_download: str
    tag_downloaded: str
    tag_loaded: str
    tag_new_viewer_request: str
    tag_raider_request: str
    tag_vip_viewer_request: str


@dataclass
class ConfSongLoader:
    enabled: bool
    twitch_channel: str
    phpsessid: str
    rspl_tags: RSPLTags
    cdlc_archive_dir: str
    destination_dir: str
    rocksmith_cdlc_dir: str
    allow_load_when_in_game: bool


@dataclass
class ConfSceneSwitcher:
    enabled: bool


@dataclass
class ConfigFile:
    config_file_path: str


@dataclass
class ConfigData:
    sniffer: ConfRockSniffer
    setlist_logger: ConfSetlistLogger
    file_manager: ConfFileManager
    song_loader: ConfSongLoader
    scene_switcher: ConfSceneSwitcher
