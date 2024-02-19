import fnmatch
import logging
import os
import pathlib
import shutil
from datetime import datetime, timedelta

from utils.exceptions import BadDirectoryError

DEFAULT_FILE_AGE_SECONDS = 9

CDLC_FILE_EXT = '*.psarc'

log = logging.getLogger()


# TODO refactor all this:
# cdlc_files = [] >> get_files(cdlc_files, directory) >> why like this? This method should just return the new set.
# or was it not recursive? And that's the why it is like that?
def get_files_from_directory(directory):
    cdlc_files = []
    get_files(cdlc_files, directory)
    return cdlc_files


def get_not_parsed_files_from_directory(directory, file_age_seconds=DEFAULT_FILE_AGE_SECONDS):
    cdlc_files = []
    get_files(cdlc_files, directory, True, file_age_seconds)
    return cdlc_files


def get_files_from_directories(directories):
    cdlc_files = []
    for directory in directories:
        if os.path.isdir(directory):
            get_files(cdlc_files, directory)
        else:
            error_msg = "Bad directory! Directory {} is not exists or could not be reached.".format(directory)
            log.error(error_msg)
            raise BadDirectoryError(error_msg, directory)

    return cdlc_files


def get_files(cdlc_files, directory, older=False, file_age_seconds=DEFAULT_FILE_AGE_SECONDS):
    for root, dir_names, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, CDLC_FILE_EXT):
            file = os.path.join(root, filename)
            if older:
                if is_file_old(file, file_age_seconds):
                    cdlc_files.append(file)
            else:
                cdlc_files.append(file)


def get_file_names_from(directory):
    cdlc_files = set()
    for root, dir_names, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, CDLC_FILE_EXT):
            cdlc_files.add(filename)
    return cdlc_files


def is_file_old(filename, old_file_age):
    file_birthday = datetime.fromtimestamp(os.path.getatime(filename))
    old_file_border = datetime.now() - timedelta(seconds=old_file_age)
    if file_birthday < old_file_border:
        return True
    return False


def get_file_path(directory, file_name):
    return os.path.join(directory, file_name)


def move_files(files, destination):
    if len(files) > 0:
        log.debug('Moving %s files to: %s | files: %s', len(files), destination, files)
        for file in files:
            move_file(file, destination)


def last_modification_time(path):
    """ Return last modified time of the path """
    try:
        return os.stat(path).st_mtime
    except FileNotFoundError:
        return 0


def move_file(file, destination):
    # TODO remove this logs? Or change to debug?
    # log.info(f"Moving file '{file}' if exists!")

    if os.path.exists(file):
        destination_file = os.path.join(destination, os.path.basename(file))
        if os.path.isfile(destination_file) and os.path.exists(destination_file):
            log.warning("File already exists, removing: %s", destination_file)
            os.remove(destination_file)
        shutil.move(file, destination)
        return True

    log.debug("File '%s' does not exists, so can not move!", file)
    return False


# TODO remove if not used
def file_datetime_formatted(filename):
    file_time = os.path.getmtime(filename)
    formatted_time = datetime.fromtimestamp(file_time)
    return formatted_time


def create_directory(directory_to_create):
    pathlib.Path(directory_to_create).mkdir(parents=True, exist_ok=True)


def create_directory_logged(directory_to_create):
    log.warning("Creating directory '%s' if not exists!", directory_to_create)
    create_directory(directory_to_create)


def replace_dlc_and_cdlc(file_name):
    return str(file_name).strip().replace('cdlc\\', '').replace('dlc\\', '')
