import re

import unicodedata

REGEXP = '[^A-Za-z0-9]+'
SPACE = ' '
ARTIST_TITLE_SEPARATOR = " - "


def normalize(text) -> str:
    if isinstance(text, str):
        # return unicodedata.normalize('NFD', text).encode('ascii', 'ignore')
        result = ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')
        return re.sub(REGEXP, SPACE, result).strip().lower()
    return text


def create_artist_minus_title(artist, title):
    if artist and title:
        return artist + ARTIST_TITLE_SEPARATOR + title
    return None


def is_blank(text: str) -> bool:
    return not is_not_blank(text)


def is_not_blank(text: str) -> bool:
    return text is not None and bool(len(text.strip()))


def escape_single_quote(text: str):
    if text is None:
        return text
    return text.replace("'", r"''")


def strtobool(value: str) -> bool:
    return value is not None and value.lower().strip() in ('1', 'y', 'yes', 'true', 't', 'on')


def time_float_to_string(time: float):
    if time is None:
        return None
    return f"{round(time, 2):.2f}"
