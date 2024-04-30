import os

import pytest

from modules.song_loader.song_data import SongData
from utils.psarc_reader import extract_psarc

# TODO change to more modern Pathlib
# from pathlib import Path
# THIS_DIR = Path(__file__).parent
# TESTDATA_PATH = THIS_DIR.parent / 'testdata'
# CDLC_PATH = TESTDATA_PATH / 'cdlc'
THIS_DIR = os.path.dirname(__file__)
TESTDATA_DIR = os.path.join(THIS_DIR, '..', 'testdata')
CDLC_DIR = os.path.join(TESTDATA_DIR, 'cdlc')


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (os.path.join(CDLC_DIR, "AC-DC_Big-Gun_v3_5_DD_p.psarc"), "AC/DC"),
        (os.path.join(CDLC_DIR, "BABYMETAL_ONE-(English)_v1_4_p.psarc"), "BABYMETAL"),
        (os.path.join(CDLC_DIR, "Depresszió_Itt-Az-Én-Időm_v1_p.psarc"), "Depresszió"),
        (os.path.join(CDLC_DIR, "Sybreed-_Doomsday-Party_v1_p.psarc"), "Sybreed ")
    ]
)
def test_artist(test_input, expected):
    song_data = SongData()

    extract_psarc(test_input, song_data, True)

    assert song_data.artist == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (os.path.join(CDLC_DIR, "AC-DC_Big-Gun_v3_5_DD_p.psarc"), "Big Gun"),
        (os.path.join(CDLC_DIR, "BABYMETAL_ONE-(English)_v1_4_p.psarc"), "THE ONE (English)"),
        (os.path.join(CDLC_DIR, "Depresszió_Itt-Az-Én-Időm_v1_p.psarc"), "Itt Az Én Időm"),
        (os.path.join(CDLC_DIR, "Sybreed-_Doomsday-Party_v1_p.psarc"), "Doomsday Party")
    ]
)
def test_title(test_input, expected):
    song_data = SongData()

    extract_psarc(test_input, song_data, True)

    assert song_data.title == expected
