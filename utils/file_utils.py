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


# TODO refactor all this:
# cdlc_files = [] >> get_files(cdlc_files, directory) >> why like this? This method should just return the new set.
# or was it not recursive? And that's the why it is like that?
def get_files_from_directory(directory):
    cdlc_files = []
    get_files(cdlc_files, directory)
    return cdlc_files


def get_not_parsed_files_from_directory(directory):
    cdlc_files = []
    get_files(cdlc_files, directory, True)
    return cdlc_files


def get_files_from_directories(directories):
    cdlc_files = []
    for directory in directories:
        get_files(cdlc_files, directory)
    return cdlc_files


def get_files(cdlc_files, directory, older=False):
    for root, dir_names, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, CDLC_FILE_EXT):
            file = os.path.join(root, filename)
            if older:
                if is_file_old(file):
                    cdlc_files.append(file)
            else:
                cdlc_files.append(file)


def get_file_names_from(directory):
    cdlc_files = set()
    for root, dir_names, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, CDLC_FILE_EXT):
            cdlc_files.add(filename)
    return cdlc_files


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
        logger.debug('Moving {} files to: {} | files: {}'.format(len(files), destination, files), module_name)
        for file in files:
            move_file(file, destination, module_name)


def last_modification_time(self, path):
    """ Return last modified time of the config """
    try:
        return os.stat(path).st_mtime
    except FileNotFoundError:
        return 0


def move_file(file, destination, module_name):
    # TODO remove this logs? Or change to debug?
    # logger.log("Moving file '{}' if exists!".format(file), module_name)

    if os.path.exists(file):
        destination_file = os.path.join(destination, os.path.basename(file))
        if os.path.isfile(destination_file) and os.path.exists(destination_file):
            logger.warning('File already exists, removing: {}'.format(destination_file), module_name)
            os.remove(destination_file)
        shutil.move(file, destination)
        return True
    else:
        logger.debug("File '{}' does not exists, so can not move!".format(file), module_name)
        return False


def file_datetime_formatted(filename):
    file_time = os.path.getmtime(filename)
    formatted_time = datetime.fromtimestamp(file_time)
    print("File datetime: {0}".format(formatted_time))  # TODO remove
    return formatted_time


# @staticmethod
def create_directory(directory_to_create):
    logger.warning("Creating directory '{}' if not exists!".format(directory_to_create))
    pathlib.Path(directory_to_create).mkdir(parents=True, exist_ok=True)
