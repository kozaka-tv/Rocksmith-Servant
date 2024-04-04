import re

import unicodedata

REGEXP = '[^A-Za-z0-9]+'
SPACE = ' '
ARTIST_TITLE_SEPARATOR = " - "


def remove_special_chars(text):
    if isinstance(text, str):
        # return unicodedata.normalize('NFD', text).encode('ascii', 'ignore')
        result = ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')
        return re.sub(REGEXP, SPACE, result).strip()


def create_artist_minus_title(artist, title):
    if artist and title:
        return artist + ARTIST_TITLE_SEPARATOR + title
    return None


def is_blank(text: str) -> bool:
    return not is_not_blank(text)


def is_not_blank(text: str) -> bool:
    return text is not None and bool(len(text.strip()))
