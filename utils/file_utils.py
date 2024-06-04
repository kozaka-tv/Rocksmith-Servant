""" Utility for mostly CDLC file handlings """

import fnmatch
import logging
import os
import pathlib
import shutil
from datetime import datetime, timedelta
from typing import Tuple

from definitions import PATTERN_CDLC_FILE_EXT, PATTERN_CDLC_INFO_FILE_EXT, \
    EXT_PSARC_INFO_JSON
from utils.string_utils import is_not_blank

DEFAULT_NOT_PARSED_FILE_AGE_SECONDS = 15

log = logging.getLogger()


def get_files_from_directory(directory):
    cdlc_files = set()
    __add_files_from_dir(cdlc_files, directory)
    return cdlc_files


def get_not_parsed_files_from_directory(directory):
    cdlc_files = set()
    __add_files_from_dir(cdlc_files, directory, True, DEFAULT_NOT_PARSED_FILE_AGE_SECONDS)
    return cdlc_files


def get_files_from_directories(directories: set) -> Tuple[set, set]:
    cdlc_files = set()
    bad_dirs = set()

    if directories:
        for directory in directories:
            if os.path.isdir(directory):
                __add_files_from_dir(cdlc_files, directory)
            else:
                log.debug('Bad directory! The directory what does not exists or could not be reached: %s', directory)
                bad_dirs.add(directory)

    return cdlc_files, bad_dirs


def __add_files_from_dir(cdlc_files: set, directory: str, older=False,
                         file_age_seconds=DEFAULT_NOT_PARSED_FILE_AGE_SECONDS):
    for root, _, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, PATTERN_CDLC_FILE_EXT):
            file = os.path.join(root, filename)
            if older:
                if is_file_old(file, file_age_seconds):
                    cdlc_files.add(file)
            else:
                cdlc_files.add(file)


def get_file_names_from(directory, extension=PATTERN_CDLC_FILE_EXT) -> set:
    log.debug('Reading file names from directory: %s', directory)
    is_info_file_ext_to_remove = extension == PATTERN_CDLC_INFO_FILE_EXT

    cdlc_files = set()

    log.debug("----- Files ------------------------------------------")
    for _, _, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, extension):
            if is_info_file_ext_to_remove:
                cdlc_files.add(filename_without_info_json_ext(filename))
            else:
                cdlc_files.add(filename)

    log.debug("-- Found %s files in directory: %s", len(cdlc_files), directory)

    return cdlc_files


def filename_without_info_json_ext(filename: str) -> str:
    return filename.partition(EXT_PSARC_INFO_JSON)[0]


def is_file_old(filename, old_file_age):
    file_birthday = datetime.fromtimestamp(os.path.getatime(filename))
    old_file_border = datetime.now() - timedelta(seconds=old_file_age)
    if file_birthday < old_file_border:
        return True
    return False


def get_file_path(directory, file_name):
    return os.path.join(directory, file_name)


def move_files_to(destination, files):
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
    if log.isEnabledFor(logging.DEBUG):
        log.debug("Moving file %s to %s if exists!", file, destination)

    if os.path.exists(file):
        destination_file = os.path.join(destination, os.path.basename(file))
        if os.path.isfile(destination_file) and os.path.exists(destination_file):
            log.warning("File already exists, removing: %s", destination_file)
            os.remove(destination_file)
        shutil.move(file, destination)
        return True

    log.debug("File '%s' does not exists, so can not move!", file)
    return False


def delete_file(directory, file):
    if os.path.exists(directory):
        file_path = os.path.join(directory, os.path.basename(file))
        if os.path.isfile(file_path) and os.path.exists(file_path):
            log.debug('Deleting file %s from %s if exists!', file, directory)
            os.remove(file_path)
        return True
    return False


def create_directory(directory_to_create):
    pathlib.Path(directory_to_create).mkdir(parents=True, exist_ok=True)


def create_directory_logged(directory_to_create):
    if is_not_blank(directory_to_create):
        log.warning("Creating directory '%s' if not exists!", directory_to_create)
        create_directory(directory_to_create)


def replace_dlc_and_cdlc(file_name):
    return str(file_name).strip().replace('cdlc\\', '').replace('dlc\\', '')
