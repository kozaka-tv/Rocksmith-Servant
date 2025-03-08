from dataclasses import dataclass

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
