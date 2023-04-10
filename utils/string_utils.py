import re

import unicodedata

REGEXP = '[^A-Za-z0-9]+'
SPACE = ' '


def remove_special_chars(text):
    # return unicodedata.normalize('NFD', text).encode('ascii', 'ignore')
    result = ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')
    result = re.sub(REGEXP, SPACE, result)
    return result
