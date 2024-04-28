from modules.song_loader.song_data import SongData


class Songs:
    def __init__(self):
        self.songs_in_archive = dict[str, SongData]()
        self.songs_need_to_be_loaded = dict[str, SongData]()  # TODO needed?
        self.songs_in_tmp = dict[str, SongData]()  # TODO needed?
        self.songs_in_rs = dict[str, SongData]()

        self.requested_songs_found_in_db = dict[str, SongData]()
        self.songs_from_archive_has_to_be_moved = dict[str, SongData]()
        self.moved_from_archive = dict[str, SongData]()
        self.missing_from_archive = dict[str, SongData]()

        # TODO temporary stuffs
        self.need_to_download = dict[str, SongData]()  # TODO needed?
