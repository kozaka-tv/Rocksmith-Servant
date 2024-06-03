import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

TMP_DIR = os.path.join(ROOT_DIR, "tmp")
CACHE_DIR = os.path.join(ROOT_DIR, "cache")
PSARC_INFO_FILE_CACHE_DIR = os.path.join(CACHE_DIR, "psarc-info-files")

EXT_CDLC_FILE = '.psarc'
EXT_PSARC_INFO_JSON = '.info.json'
EXT_CDLC_INFO_FILE = EXT_CDLC_FILE + EXT_PSARC_INFO_JSON

ASTERISK = '*'
PATTERN_CDLC_FILE_EXT = ASTERISK + EXT_CDLC_FILE
PATTERN_CDLC_INFO_FILE_EXT = ASTERISK + EXT_CDLC_INFO_FILE

KEY_VALUES_OF_AN_OFFICIAL_CDLC = (3, 4)
