from dataclasses import dataclass, field
from typing import Optional

from common.definitions import KEY_VALUES_OF_AN_OFFICIAL_CDLC
from modules.servant.song_loader.dataclasses.artist_title import ArtistTitle


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
        def format_attribute(name, value):
            return f"{name}={value}" if value else None

        attributes = [
            format_attribute("song_filename", self.song_filename),
            format_attribute("artist_title", self.artist_title),
            format_attribute("rspl_request_id", self.rspl_request_id),
            format_attribute("cdlc_id", self.cdlc_id),
            format_attribute("rspl_song_id", self.rspl_song_id),
            format_attribute("rspl_official", self.rspl_official),
            format_attribute("rspl_position", self.rspl_position),
            format_attribute("tags", self.tags)
        ]

        attributes_str = ", ".join(attr for attr in attributes if attr)
        return f"<SongData: {attributes_str}>"
