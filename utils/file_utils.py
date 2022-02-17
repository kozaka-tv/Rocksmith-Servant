import fnmatch
import os
import pathlib
import shutil
from datetime import datetime, timedelta

from utils import logger

FILE_AGE = 15
LOG_DIR = 'log'
CDLC_FILE_EXT = '*.psarc'


def create_log_dir():
    pathlib.Path(os.path.join(LOG_DIR)).mkdir(parents=True, exist_ok=True)


def create_cdlc_dir():
    pathlib.Path(os.path.join(LOG_DIR)).mkdir(parents=True, exist_ok=True)


def get_files_from_directory(directory, module_name, pattern):
    cdlc_files = []
    get_files(cdlc_files, directory, module_name, pattern)
    return cdlc_files


def get_not_parsed_files_from_directory(directory, module_name, pattern):
    cdlc_files = []
    get_files(cdlc_files, directory, module_name, pattern, True)
    return cdlc_files


def get_files_from_directories(directories, module_name, pattern):
    cdlc_files = []
    for directory in directories:
        get_files(cdlc_files, directory, module_name, pattern)
    return cdlc_files


def get_files(cdlc_files, directory, module_name, pattern, older=False):
    for root, dir_names, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, pattern):
            file = os.path.join(root, filename)
            if older:
                if is_file_old(file):
                    cdlc_files.append(file)
            else:
                cdlc_files.append(file)


def is_file_old(filename):
    file_datetime = datetime.fromtimestamp(os.path.getmtime(filename))
    # TODO maybe this FILE_AGE should come from the module. To define in the module what is an aged file!?
    cutoff = datetime.now() - timedelta(seconds=FILE_AGE)
    if file_datetime < cutoff:
        return True
    return False


def get_file_path(directory, file_name):
    return os.path.join(directory, file_name)


def move_files(files, destination, module_name):
    if len(files) > 0:
        logger.log('Moving {} files to: {}'.format(len(files), destination), module_name)
        for file in files:
            logger.log('Moving: {}'.format(file), module_name)
            destination_file = os.path.join(destination, os.path.basename(file))
            if os.path.isfile(destination_file):
                logger.warning('File already exists, removing: {}'.format(destination_file), module_name)
                os.remove(destination_file)

            shutil.move(file, destination)


def file_datetime_formatted(filename):
    file_time = os.path.getmtime(filename)
    formatted_time = datetime.fromtimestamp(file_time)
    print("File datetime: {0}".format(formatted_time))  # TODO remove
    return formatted_time
