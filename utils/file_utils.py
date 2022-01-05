import os
import pathlib

LOG_DIR = 'log'


def create_log_dir():
    pathlib.Path(os.path.join(LOG_DIR)).mkdir(parents=True, exist_ok=True)


def create_import_dir():
    pathlib.Path(os.path.join(LOG_DIR)).mkdir(parents=True, exist_ok=True)
