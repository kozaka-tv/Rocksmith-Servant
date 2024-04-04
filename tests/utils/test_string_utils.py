import pytest

from utils import string_utils


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (None, None),
        ("", ""),
        (" ", ""),

        ("Metallica - Cyanide", "Metallica Cyanide"),
        ("Creeping Death", "Creeping Death"),

        ("Depresszió - Itt Az Én Időm", "Depresszio Itt Az En Idom"),
        ("Alvin és a Mókusok - Kurva Élet", "Alvin es a Mokusok Kurva Elet"),
        ("Ill Niño - If You Still Hate Me", "Ill Nino If You Still Hate Me"),
        ("Daði Freyr - Think About Things", "Da i Freyr Think About Things"),
        ("L'Impératrice - L'Impératrice", "L Imperatrice L Imperatrice"),
        ("L'Impératrice - Fou", "L Imperatrice Fou"),
        ("Nirvana/Sungha Jung - Come As You Are", "Nirvana Sungha Jung Come As You Are"),
        ("The Dillinger Escape Plan - 43% Burnt (Ramen's Ver)", "The Dillinger Escape Plan 43 Burnt Ramen s Ver"),

        ("Guns N' Roses - Don`t Cry (Tonight)", "Guns N Roses Don t Cry Tonight"),
        ("Swallow The Sun - Swallow (Horror pt.1)", "Swallow The Sun Swallow Horror pt 1"),
    ]
)
def test_remove_special_chars(test_input, expected):
    actual = string_utils.remove_special_chars(test_input)

    assert actual == expected


@pytest.mark.parametrize(
    "artist, title, expected",
    [
        (None, None, None),
        ("", None, None),
        (None, "", None),
        ("", "", None),
        ("ARTIST", None, None),
        ("ARTIST", "", None),
        (None, "TITLE", None),
        ("", "TITLE", None),
        ("ARTIST", "TITLE", "ARTIST - TITLE"),
    ]
)
def test_create_artist_minus_title(artist, title, expected):
    actual = string_utils.create_artist_minus_title(artist, title)

    assert actual == expected
