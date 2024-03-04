import os
from enum import unique, Enum

from utils import string_utils


# TODO do we need this state at all?
@unique
class State(Enum):
    # -- New request on the rsplaylist
    NEW_REQUEST = 10
    # -- Could not be found in the archive and not loaded in the game
    TO_DOWNLOAD = 20
    # --
    FOUND_IN_ARCHIVE = 30
    MOVED_FROM_ARCHIVE = 31
    LOADED = 32
    # --
    OUT_FROM_THE_PLAYLIST = 40


class SongData:

    def __init__(self, rspl_request_id=None, cdlc_id=None, rspl_song_id=None, artist=None, title=None,
                 song_file_name=None):
        self.rspl_request_id = rspl_request_id  # id of the request on RSPL
        self.cdlc_id = cdlc_id
        self.rspl_song_id = rspl_song_id  # id of the request on RSPL
        self.artist = artist
        self.title = title
        self.artist_title = string_utils.create_artist_minus_title(artist, title)

        self.rspl_official = None
        self.rspl_position = None
        self.song_file_name = song_file_name
        # --
        self.state = State.NEW_REQUEST
        self.tags = set()
        # --
        self.found_in_db = False
        self.loaded_under_the_game = False
        self.missing = False

    @property
    def is_official(self):
        if self.rspl_official is None:
            return False
        # TODO is there any other official numbers? Maybe only 0 means non official?
        return self.rspl_official == 3 or self.rspl_official == 4

    @property
    def is_missing(self):
        return self.missing

    # TODO rspl_request_id? or cdlc_id? or something else?
    def __eq__(self, other):
        return self.rspl_request_id == other.rspl_request_id

    def __hash__(self):
        return hash(self.rspl_request_id)

    def __repr__(self):
        return f"{os.linesep}<SongData: " \
               f"rspl_request_id={self.rspl_request_id}, " \
               f"rspl_song_id={self.rspl_song_id}, " \
               f"cdlc_id={self.cdlc_id}, " \
               f"artist={self.artist}, " \
               f"title={self.title}, " \
               f"artist_title={self.artist_title}, " \
               f"rspl_official={self.rspl_official}, " \
               f"song_file_name={self.song_file_name}" \
               f">"

# TODO create a test out from this later
# s1 = SongData(1, 555, 'asd')
# s2 = SongData(2, 666, 'qwe')
# s3 = SongData(1, 777, '123')

# songs_from_archive_need_to_be_loaded = {s1, s2, s3}
# print(songs_from_archive_need_to_be_loaded)
# output:
# {
# <SongData: rspl_request_id=1, cdlc_id=555, song_file_name=asd>,
# <SongData: rspl_request_id=2, cdlc_id=666, song_file_name=qwe>}
