from modules.song_loader.song_data import SongData


class Songs:
    def __init__(self):
        self.archive = set[SongData]()

        self.loaded_into_rs = set()
        self.loaded_into_rs_with_song_data = set[SongData]()

        self.songs_from_archive_need_to_be_loaded = set()
        self.need_to_download = set()
        self.moved_from_archive = set()
        self.missing_from_archive = set()
