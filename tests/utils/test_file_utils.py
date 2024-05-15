import pytest

from utils import file_utils


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
