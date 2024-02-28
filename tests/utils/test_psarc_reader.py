import pytest

from modules.song_loader.song_data import SongData
from utils.psarc_reader import extract_psarc


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("..\\tests\\test_data\\AC-DC_Big-Gun_v3_5_DD_p.psarc", "AC/DC"),
        ("..\\tests\\test_data\\BABYMETAL_ONE-(English)_v1_4_p.psarc", "BABYMETAL"),
        ("..\\tests\\test_data\\Depresszió_Itt-Az-Én-Időm_v1_p.psarc", "Depresszió")
    ]
)
def test_artist(test_input, expected):
    song_data = SongData()

    extract_psarc(test_input, song_data)

    assert song_data.artist == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("..\\tests\\test_data\\AC-DC_Big-Gun_v3_5_DD_p.psarc", "Big Gun"),
        ("..\\tests\\test_data\\BABYMETAL_ONE-(English)_v1_4_p.psarc", "THE ONE (English)"),
        ("..\\tests\\test_data\\Depresszió_Itt-Az-Én-Időm_v1_p.psarc", "Itt Az Én Időm")
    ]
)
def test_title(test_input, expected):
    song_data = SongData()

    extract_psarc(test_input, song_data)

    assert song_data.title == expected
