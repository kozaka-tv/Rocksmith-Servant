from dataclasses import dataclass, field
from typing import Optional

from common.definitions import KEY_VALUES_OF_AN_OFFICIAL_CDLC
from utils.string_utils import normalize


@dataclass(slots=True)
class ArtistTitle:
    artist: str
    title: str

    def artist_normalized(self) -> str:
        return normalize(self.artist)

    def title_normalized(self) -> str:
        return normalize(self.title)

    def __repr__(self):
        rep = '<ArtistTitle: '
        rep += f"artist={self.artist}, "
        rep += f"title={self.title}"
        rep += ">"

        return rep


@dataclass(slots=True)
class SongData(object):
    song_filename: Optional[str] = None

    artist_title: Optional[ArtistTitle] = None

    rspl_request_id: Optional[int] = None  # id of the request on RSPL
    cdlc_id: Optional[int] = None
    rspl_song_id: Optional[int] = None  # id of the request on RSPL
    rspl_official: Optional[str] = None
    rspl_position: Optional[str] = None

    tags: set[str] = field(default_factory=set)

    @property
    def is_official(self):
        return self.rspl_official in KEY_VALUES_OF_AN_OFFICIAL_CDLC

    def __repr__(self):
        rep = '<SongData: '

        if self.song_filename:
            rep += f"song_filename={self.song_filename}, "

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
