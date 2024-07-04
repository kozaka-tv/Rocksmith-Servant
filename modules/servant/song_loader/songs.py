import dataclasses

from modules.servant.song_loader.song_data import SongData


@dataclasses.dataclass
class Songs:
    def __init__(self):
        self.songs_in_archive = dict[str, SongData]()

        self.songs_in_download = dict[str, SongData]()
        self.songs_in_import = dict[str, SongData]()
        self.songs_in_tmp = dict[str, SongData]()

        self.songs_in_rs = dict[str, SongData]()

        self.requested_songs_found_in_db = dict[str, SongData]()
        self.songs_from_archive_has_to_be_moved = dict[str, SongData]()
        self.moved_from_archive = dict[str, SongData]()
        self.missing_from_archive = dict[str, SongData]()

        self.need_to_download = dict[str, SongData]()
        self.songs_need_to_be_loaded = dict[str, SongData]()
