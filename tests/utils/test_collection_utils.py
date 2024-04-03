import pytest

from utils import collection_utils


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (None, True),
        (set(), True),
        ([1, 2], False)
    ]
)
def test_is_empty(test_input, expected):
    assert collection_utils.is_empty(test_input) == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (None, False),
        (set(), False),
        ([1, 2], True)
    ]
)
def test_is_not_empty(test_input, expected):
    assert collection_utils.is_not_empty(test_input) == expected
