import os


TMP_DIR_NAME = "tmp"
CACHE_DIR_NAME = "cache"
PSARC_INFO_FILES_DIR_NAME = "psarc-info-files"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(ROOT_DIR, TMP_DIR_NAME)
CACHE_DIR = os.path.join(ROOT_DIR, CACHE_DIR_NAME)
PSARC_INFO_FILE_CACHE_DIR = os.path.join(CACHE_DIR, PSARC_INFO_FILES_DIR_NAME)
