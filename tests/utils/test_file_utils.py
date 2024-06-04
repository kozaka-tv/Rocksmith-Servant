import os

import pytest

from base_test import TEST_CDLC_DIR
from utils import file_utils

BAD_DIR = 'some_bad_dir'
ANOTHER_BAD_DIR = 'another_bad_dir'


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ('', ''),
        ('filename_without_extension', 'filename_without_extension'),
        ('filename.psarc', 'filename.psarc'),
        ('filename.psarc.info.json', 'filename.psarc'),
    ]
)
def test_filename_without_info_json_ext(test_input, expected):
    assert file_utils.filename_without_info_json_ext(test_input) == expected


def test_get_files_from_directories__with_none():
    # noinspection PyTypeChecker
    actual = file_utils.get_files_from_directories(None)

    assert actual[0] == set()
    assert actual[1] == set()


def test_get_files_from_directories__with_empty_directories():
    actual = file_utils.get_files_from_directories(set())

    assert actual[0] == set()
    assert actual[1] == set()


@pytest.mark.parametrize(
    "test_input, expected",
    [
        # root dir
        ({''},
         (
                 {
                     'Sybreed-_Doomsday-Party_v1_p.psarc',
                     'Depresszió_Itt-Az-Én-Időm_v1_p.psarc',
                     'BABYMETAL_ONE-(English)_v1_4_p.psarc',
                     'BABYMETAL-Tom-Morello_METALI---feat-Tom-Morello_v1_1_p.psarc',
                     'AC-DC_Big-Gun_v3_5_DD_p.psarc',

                     'Beatles_And-I-Love-Her_v1_p.psarc',
                     'BABYMETAL-and-Electric-Callboy_RATATATA_v1_2_DD_p.psarc',

                     'Svalbard_Defiance_v1_0_p.psarc',
                     'Saxon_Madame-Guillotine_v1_p.psarc',
                     'Meshuggah_War_v1_p.psarc',
                 },
                 set())
         ),

        # one bad dir
        ({BAD_DIR},
         (set(), {BAD_DIR})),

        # only one empty dir
        ({'empty_dir'}, (set(), set())),

        # only the download_1 dir
        ({'download_1'},
         (
                 {
                     'Beatles_And-I-Love-Her_v1_p.psarc',
                     'BABYMETAL-and-Electric-Callboy_RATATATA_v1_2_DD_p.psarc',
                 },
                 set())
         ),

        # only the download_2 dir
        ({'download_2'},
         (
                 {
                     'Svalbard_Defiance_v1_0_p.psarc',
                     'Saxon_Madame-Guillotine_v1_p.psarc',
                     'Meshuggah_War_v1_p.psarc',
                 },
                 set())
         ),

        # download_1 and download_2 dir
        ({'download_1', 'download_2'},
         (
                 {
                     'Beatles_And-I-Love-Her_v1_p.psarc',
                     'BABYMETAL-and-Electric-Callboy_RATATATA_v1_2_DD_p.psarc',

                     'Svalbard_Defiance_v1_0_p.psarc',
                     'Saxon_Madame-Guillotine_v1_p.psarc',
                     'Meshuggah_War_v1_p.psarc',
                 },
                 set())
         ),

        # download_1, a bad dir and download_2 dir
        ({'download_1', BAD_DIR, 'download_2'},
         (
                 {
                     'Beatles_And-I-Love-Her_v1_p.psarc',
                     'BABYMETAL-and-Electric-Callboy_RATATATA_v1_2_DD_p.psarc',

                     'Svalbard_Defiance_v1_0_p.psarc',
                     'Saxon_Madame-Guillotine_v1_p.psarc',
                     'Meshuggah_War_v1_p.psarc',
                 },
                 {BAD_DIR})
         ),

        # download_1, a bad dir, download_2 dir and an another bad dir
        ({'download_1', BAD_DIR, 'download_2', ANOTHER_BAD_DIR},
         (
                 {
                     'Beatles_And-I-Love-Her_v1_p.psarc',
                     'BABYMETAL-and-Electric-Callboy_RATATATA_v1_2_DD_p.psarc',

                     'Svalbard_Defiance_v1_0_p.psarc',
                     'Saxon_Madame-Guillotine_v1_p.psarc',
                     'Meshuggah_War_v1_p.psarc',
                 },
                 {BAD_DIR, ANOTHER_BAD_DIR})
         ),

    ]
)
def test_get_files_from_directories(test_input, expected: tuple):
    dirs = set()
    for test_input_dir in test_input:
        dirs.add(os.path.join(TEST_CDLC_DIR, test_input_dir))

    actual = file_utils.get_files_from_directories(dirs)

    __assert_found_cdlc_files(actual, expected)
    __assert_found_bad_dirs(actual, expected)


def __assert_found_cdlc_files(actual, expected):
    __assert_tuple_element_of(0, actual, expected)


def __assert_found_bad_dirs(actual, expected):
    __assert_tuple_element_of(1, actual, expected)


def __assert_tuple_element_of(element: int, actual, expected):
    counter = 0
    for filename in actual[element]:
        assert os.path.basename(filename) in expected[element]
        counter += 1
    assert counter == len(expected[element])
