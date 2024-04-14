from enum import unique, Enum

from utils import string_utils


@unique
# TODO do we need this state at all?
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
        self.song_file_name = song_file_name

        self.artist_title = string_utils.create_artist_minus_title(artist, title)

        # --
        self.rspl_official = None
        self.rspl_position = None
        # --
        self.state = State.NEW_REQUEST
        self.tags = set()
        # --
        self.found_in_db = False
        self.loaded_under_the_game = False
        self.missing = False

    @property
    def is_official(self):
        # TODO is there any other official numbers? Maybe only 0 means non official?
        return 3 == self.rspl_official or 4 == self.rspl_official

    @property
    def is_missing(self):
        return self.missing

    # TODO rspl_request_id? or cdlc_id? or something else?
    # def __eq__(self, other):
    # return self.rspl_request_id == other.rspl_request_id
    # return self.song_file_name == other.song_file_name

    # def __hash__(self):
    #     return hash(self.rspl_request_id)

    def __repr__(self):
        # TODO extend with other properties?
        # TODO write out only variables existing? Do not add None-s?
        representation = '<SongData: '
        if self.rspl_request_id:
            representation += f"rspl_request_id={self.rspl_request_id}, "
        if self.cdlc_id:
            representation += f"cdlc_id={self.cdlc_id}, "
        if self.rspl_song_id:
            representation += f"rspl_song_id={self.rspl_song_id}, "
        if self.artist:
            representation += f"artist={self.artist}, "
        if self.title:
            representation += f"title={self.title}, "
        if self.song_file_name:
            representation += f"song_file_name={self.song_file_name}, "
        if self.artist_title:
            representation += f"artist_title={self.artist_title}, "
        if self.rspl_official:
            representation += f"rspl_official={self.rspl_official}, "
        if self.rspl_position:
            representation += f"rspl_position={self.rspl_position}, "
        if self.state:
            representation += f"state={self.state}, "
        if self.tags:
            representation += f"tags={self.tags}"
        if self.found_in_db:
            representation += f"found_in_db={self.found_in_db}, "
        if self.loaded_under_the_game:
            representation += f"loaded_under_the_game={self.loaded_under_the_game}, "
        if self.missing:
            representation += f"missing={self.missing}, "

        representation += ">"

        return representation
