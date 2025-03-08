import os

import pytest

from modules.servant.song_loader.dataclasses.song_data import SongData
from tests.base_test import TEST_CDLC_DIR
from utils.psarc_reader import extract

# If you want to keep the info.json files, set this to True
KEEP_INFO_FILES = False


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (os.path.join(TEST_CDLC_DIR, "AC-DC_Big-Gun_v3_5_DD_p.psarc"), "AC/DC"),
        (os.path.join(TEST_CDLC_DIR, "BABYMETAL_ONE-(English)_v1_4_p.psarc"), "BABYMETAL"),
        (os.path.join(TEST_CDLC_DIR, "Depresszió_Itt-Az-Én-Időm_v1_p.psarc"), "Depresszió"),
        (os.path.join(TEST_CDLC_DIR, "Sybreed-_Doomsday-Party_v1_p.psarc"), "Sybreed "),
        (os.path.join(TEST_CDLC_DIR, "BABYMETAL-Tom-Morello_METALI---feat-Tom-Morello_v1_1_p.psarc"),
         "BABYMETAL, Tom Morello")
    ]
)
def test_artist(test_input, expected):
    song_data = SongData()

    extract(test_input, song_data, KEEP_INFO_FILES)

    assert song_data.artist_title.artist == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (os.path.join(TEST_CDLC_DIR, "AC-DC_Big-Gun_v3_5_DD_p.psarc"), "Big Gun"),
        (os.path.join(TEST_CDLC_DIR, "BABYMETAL_ONE-(English)_v1_4_p.psarc"), "THE ONE (English)"),
        (os.path.join(TEST_CDLC_DIR, "Depresszió_Itt-Az-Én-Időm_v1_p.psarc"), "Itt Az Én Időm"),
        (os.path.join(TEST_CDLC_DIR, "Sybreed-_Doomsday-Party_v1_p.psarc"), "Doomsday Party"),
        (os.path.join(TEST_CDLC_DIR, "BABYMETAL-Tom-Morello_METALI---feat-Tom-Morello_v1_1_p.psarc"),
         "METALI!! - feat. Tom Morello"),
    ]
)
def test_title(test_input, expected):
    song_data = SongData()

    extract(test_input, song_data, KEEP_INFO_FILES)

    assert song_data.artist_title.title == expected
