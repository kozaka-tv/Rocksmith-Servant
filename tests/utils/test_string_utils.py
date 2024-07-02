import pytest

from utils import string_utils


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (None, None),
        ("", ""),
        (" ", ""),

        ("Metallica - Cyanide", "metallica cyanide"),
        ("Creeping Death", "creeping death"),

        ("Depresszió - Itt Az Én Időm", "depresszio itt az en idom"),
        ("Alvin és a Mókusok - Kurva Élet", "alvin es a mokusok kurva elet"),
        ("Ill Niño - If You Still Hate Me", "ill nino if you still hate me"),
        ("Daði Freyr - Think About Things", "da i freyr think about things"),
        ("L'Impératrice - L'Impératrice", "l imperatrice l imperatrice"),
        ("L'Impératrice - Fou", "l imperatrice fou"),
        ("Nirvana/Sungha Jung - Come As You Are", "nirvana sungha jung come as you are"),
        ("The Dillinger Escape Plan - 43% Burnt (Ramen's Ver)", "the dillinger escape plan 43 burnt ramen s ver"),

        ("Guns N' Roses - Don`t Cry (Tonight)", "guns n roses don t cry tonight"),
        ("Swallow The Sun - Swallow (Horror pt.1)", "swallow the sun swallow horror pt 1"),

        ("Молчат Дома / Molchat Doma - Танцевать / Tancevat", "molchat doma tancevat"),
    ]
)
def test_normalize(test_input, expected):
    actual = string_utils.normalize(test_input)

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


@pytest.mark.parametrize(
    "text, expected",
    [
        (None, True),
        ("", True),
        (" ", True),
        ("TEXT", False),
    ]
)
def test_is_blank(text, expected):
    actual = string_utils.is_blank(text)

    assert actual == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        (None, False),
        ("", False),
        (" ", False),
        ("TEXT", True),
    ]
)
def test_is_not_blank(text, expected):
    actual = string_utils.is_not_blank(text)

    assert actual == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        (None, None),
        ("", ""),
        (" ", " "),
        ("TEXT", "TEXT"),
        ("TEXT's", "TEXT''s"),
        ("TEXT's more'text", "TEXT''s more''text"),
        ("TEXT and just a '", "TEXT and just a ''"),
    ]
)
def test_escape_single_quote(text, expected):
    actual = string_utils.escape_single_quote(text)

    assert actual == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        (None, False),
        ("", False),
        (" ", False),
        ("TEXT", False),
        (" TEXT ", False),

        ("0", False),
        (" 0 ", False),
        ("n", False),
        ("no", False),
        ("false", False),
        ("False", False),

        ("1", True),
        (" 1 ", True),
        ("y", True),
        ("yes", True),
        ("true", True),
        ("t", True),
        ("on", True),
    ]
)
def test_strtobool(text, expected):
    actual = string_utils.strtobool(text)

    assert actual == expected


@pytest.mark.parametrize(
    "time, expected",
    [
        (None, None),
        (3, '3.00'),
        (5.1, '5.10'),
        (6.05, '6.05'),
        (10.123, '10.12'),
    ]
)
def test_time_float_to_string(time, expected):
    actual = string_utils.time_float_to_string(time)

    assert actual == expected
