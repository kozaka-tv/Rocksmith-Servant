class Songs:
    def __init__(self):
        # TODO song_data_set is now a list of song_data which are loaded (moved) from archive to RS
        #   rename to setlist? --> this should be actually a list of all the requested, really played songs.
        #   So it should contain all the RS playlist requests, with different state. Or just have like this? IDK
        self.song_data_set = set()
        self.loaded_into_rs = set()
        # self.archive = set() # TODO needed?
        self.need_to_download = set()
        self.moved_from_archive = set()
        self.missing_from_archive = set()
