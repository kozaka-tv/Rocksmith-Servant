import os
from enum import unique, Enum


class Songs:
    def __init__(self):
        self.archive = set()
        self.requests = set()
        self.loaded = set()
        self.missing = set()
        # TODO this set is maybe not needed!
        self.song_data_set = set()


@unique
class State(Enum):
    # -- New request on the playlist
    NEW_REQUEST = 10
    # -- Could not found in the archive and not loaded in the game
    TO_DOWNLOAD = 20
    # --
    FOUND_IN_ARCHIVE = 30
    MOVED_FROM_ARCHIVE = 31
    LOADED = 32
    # --
    OUT_FROM_THE_PLAYLIST = 40


class SongData:
    def __init__(self, sr_id, cdlc_id, song_file_name=None):
        self.sr_id = sr_id
        self.cdlc_id = cdlc_id
        self.song_file_name = song_file_name
        # --
        self.state = State.NEW_REQUEST
        # --
        self.found_in_db = False
        self.loaded_under_the_game = False

    # TODO sr_id? or cdlc_id? or something else?
    def __eq__(self, other):
        return self.sr_id == other.sr_id

    def __hash__(self):
        return hash(self.sr_id)

    def __repr__(self):
        return os.linesep + '<SongData: sr_id={}, cdlc_id={}, song_file_name={}>'.format(self.sr_id,
                                                                                         self.cdlc_id,
                                                                                         self.song_file_name)


# TODO remove this later if the eq is decided!
s1 = SongData(1, 555, 'asd')
s2 = SongData(2, 666, 'qwe')
s3 = SongData(1, 777, '123')

song_data_set = {s1, s2, s3}
print(song_data_set)
# output: {<Person tom>, <Person mary>}
