import dataclasses
from typing import Dict

from modules.servant.song_loader.song_data import SongData


@dataclasses.dataclass
class Songs:
    songs_in_archive: Dict[str, SongData] = dataclasses.field(default_factory=dict)

    songs_in_download: dict[str, SongData] = dataclasses.field(default_factory=dict)
    songs_in_import: dict[str, SongData] = dataclasses.field(default_factory=dict)
    songs_in_tmp: dict[str, SongData] = dataclasses.field(default_factory=dict)

    songs_in_rs: dict[str, SongData] = dataclasses.field(default_factory=dict)

    requested_songs_found_in_db: dict[str, SongData] = dataclasses.field(default_factory=dict)
    songs_from_archive_has_to_be_moved: dict[str, SongData] = dataclasses.field(default_factory=dict)
    moved_from_archive: dict[str, SongData] = dataclasses.field(default_factory=dict)
    missing_from_archive: dict[str, SongData] = dataclasses.field(default_factory=dict)

    need_to_download: dict[str, SongData] = dataclasses.field(default_factory=dict)
    songs_need_to_be_loaded: dict[str, SongData] = dataclasses.field(default_factory=dict)
