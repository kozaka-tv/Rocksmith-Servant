from modules.song_loader.song_data import SongData


class Songs:
    def __init__(self):
        self.songs_in_archive = dict[str, SongData]()

        self.songs_in_download = dict[str, SongData]()  # TODO needed?
        self.songs_in_import = dict[str, SongData]()  # TODO needed?
        self.songs_in_tmp = dict[str, SongData]()  # TODO needed?

        self.songs_in_rs = dict[str, SongData]()

        self.requested_songs_found_in_db = dict[str, SongData]()
        self.songs_from_archive_has_to_be_moved = dict[str, SongData]()
        self.moved_from_archive = dict[str, SongData]()
        self.missing_from_archive = dict[str, SongData]()

        # TODO temporary stuffs
        # TODO needed? --> This is only max an Artist - Song list as I do not know, what the filename is
        #   means, this is actually a RSPL list (only what is need to be downloaded).
        self.need_to_download = dict[str, SongData]()
        self.songs_need_to_be_loaded = dict[str, SongData]()  # TODO needed?
