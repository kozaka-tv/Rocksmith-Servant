import re

import unicodedata

REGEXP = '[^A-Za-z0-9]+'
SPACE = ' '
ARTIST_TITLE_SEPARATOR = " - "


def remove_special_chars(text):
    # return unicodedata.normalize('NFD', text).encode('ascii', 'ignore')
    result = ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')
    result = re.sub(REGEXP, SPACE, result)
    return result


def create_artist_minus_title(artist, title):
    if artist and title:
        return artist + ARTIST_TITLE_SEPARATOR + title
    return None
