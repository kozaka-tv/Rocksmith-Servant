from dataclasses import dataclass
from typing import List, Optional


# Define the data class for one ODLC
@dataclass
class RSPLOwnedDLC:
    id: int
    artist_name: str
    title: str
    owned: bool


@dataclass
class OwnedDLC:
    rspl_owned_dlc_id: int
    artist_name: str
    title: str
    owned: bool
    song_filename: Optional[str] = None
    cdlc_id: Optional[int] = None


# Define the data class for all the ODLCs
@dataclass
class OwnedDLCs:
    data: List[OwnedDLC]
    total_count: int
    owned_count: int
