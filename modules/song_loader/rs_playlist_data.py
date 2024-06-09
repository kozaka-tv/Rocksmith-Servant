from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class Viewer:
    username: str
    twitch_id: int
    badges: List[str]
    present: bool
    inactive: bool
    inactive_time: int


@dataclass
class DlcSet:
    id: int
    cdlc_id: int
    artist: str
    artist_id: int
    title: str
    album: str
    tuning: int
    parts: Optional[str]
    dd: bool
    official: int
    creator: str
    estimated_length: int
    trr_url: Optional[str]
    updated: int
    downloads: int
    tuning_name: str
    paths: int
    paths_string: str


@dataclass
class PlaylistItem:
    id: int
    vip: bool
    position: int
    string: str
    tags: List[str]
    request_timestamp: int
    viewer: Viewer
    dlc_set: List[DlcSet]


@dataclass
class ChannelTag:
    name: str
    icon: str
    color: str
    user: bool


@dataclass
class RsPlaylist:
    playlist: List[PlaylistItem]
    channel_tags: Dict[str, ChannelTag]
