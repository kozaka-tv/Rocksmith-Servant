from definitions import KEY_VALUES_OF_AN_OFFICIAL_CDLC
from utils import string_utils


class SongData:

    def __init__(self, rspl_request_id=None, cdlc_id=None, rspl_song_id=None, artist=None, title=None,
                 song_filename=None):

        self.song_filename = song_filename

        self.artist = artist
        self.title = title
        self.artist_title = string_utils.create_artist_minus_title(artist, title)

        self.rspl_request_id = rspl_request_id  # id of the request on RSPL
        self.cdlc_id = cdlc_id
        self.rspl_song_id = rspl_song_id  # id of the request on RSPL
        self.rspl_official = None
        self.rspl_position = None

        self.tags = set()

    @property
    def is_official(self):
        return self.rspl_official in KEY_VALUES_OF_AN_OFFICIAL_CDLC

    def __repr__(self):
        rep = '<SongData: '

        if self.song_filename:
            rep += f"song_filename={self.song_filename}, "

        if self.artist:
            rep += f"artist={self.artist}, "
        if self.title:
            rep += f"title={self.title}, "
        if self.artist_title:
            rep += f"artist_title={self.artist_title}, "

        if self.rspl_request_id:
            rep += f"rspl_request_id={self.rspl_request_id}, "
        if self.cdlc_id:
            rep += f"cdlc_id={self.cdlc_id}, "
        if self.rspl_song_id:
            rep += f"rspl_song_id={self.rspl_song_id}, "
        if self.rspl_official:
            rep += f"rspl_official={self.rspl_official}, "
        if self.rspl_position:
            rep += f"rspl_position={self.rspl_position}, "

        if self.tags:
            rep += f"tags={self.tags}"

        rep += ">"

        return rep
