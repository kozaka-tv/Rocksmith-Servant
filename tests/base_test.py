import os

# TODO change to more modern Pathlib
# from pathlib import Path
# TEST_DIR = Path(__file__).parent
# TESTDATA_PATH = TEST_DIR.parent / 'testdata'
# CDLC_PATH = TESTDATA_PATH / 'cdlc'
TEST_DIR = os.path.dirname(__file__)
TESTDATA_DIR = os.path.join(TEST_DIR, 'testdata')

CDLC_DIR = os.path.join(TESTDATA_DIR, 'cdlc')
INFO_FILES_DIR = os.path.join(TESTDATA_DIR, 'psarc-info-files')
