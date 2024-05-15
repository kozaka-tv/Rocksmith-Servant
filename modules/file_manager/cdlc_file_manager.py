import datetime
import logging
import math

from definitions import TMP_DIR, TMP_DIR_NAME
from utils import file_utils
from utils.collection_utils import repr_in_multi_line, is_not_empty
from utils.exceptions import BadDirectoryError

HEARTBEAT = 1
HEARTBEAT_NOT_PARSED = 5

log = logging.getLogger()


class FileManager:
    def __init__(self, config_data):
        """
        File manager to manage CDLC files
        """
        self.enabled = config_data.file_manager.enabled
        if self.enabled:
            self.last_run = datetime.datetime.now()
            self.last_run_not_parsed = self.last_run
            self.source_directories = config_data.file_manager.source_directories
            self.destination_directory = config_data.file_manager.destination_directory
            self.using_cfsm = config_data.file_manager.using_cfsm

    def update_config(self, config_data):
        self.enabled = config_data.file_manager.enabled
        self.source_directories = config_data.file_manager.source_directories
        self.destination_directory = config_data.file_manager.destination_directory
        self.using_cfsm = config_data.file_manager.using_cfsm

    def run(self):
        if self.enabled:
            if self.__beat_last_run_not_parsed():
                self.__move_non_parsed_files_to_tmp_dir()

            elif self.__beat_last_run():
                log.debug("Scan and move files from %s and source dirs...", TMP_DIR_NAME)
                self.__move_files_to_destination_dir(self.__scan_cdlc_files_in_tmp())
                self.__move_files_to_destination_dir(self.__scan_cdlc_files_in_source_dirs())

                self.last_run = datetime.datetime.now()

    def __move_non_parsed_files_to_tmp_dir(self):
        log.debug("Scan and move files which were not parsed by CFSM.")
        moved = self.__move_not_parsed_files_to_tmp()
        if moved:
            log.debug("Found non parsed files which were now moved... ")
            self.last_run = datetime.datetime.now()
            self.last_run_not_parsed = self.last_run
        else:
            log.debug("Nothing moved... ")
            self.last_run = datetime.datetime.now()
            self.last_run_not_parsed = self.last_run

    def __beat_last_run(self):
        return math.floor((datetime.datetime.now() - self.last_run).seconds) >= HEARTBEAT

    def __beat_last_run_not_parsed(self):
        return math.floor((datetime.datetime.now() - self.last_run_not_parsed).seconds) >= HEARTBEAT_NOT_PARSED

    def __move_not_parsed_files_to_tmp(self):
        non_parsed_files = self.__scan_cdlc_files_in_destination_dir()

        if is_not_empty(non_parsed_files):
            log.warning(
                "Found %s file(s) in %s dir which one(s) were not yet parsed so I moving them to %s now! Files: %s"
                , len(non_parsed_files), self.destination_directory, TMP_DIR_NAME, repr_in_multi_line(non_parsed_files))
            file_utils.move_files_to(TMP_DIR, non_parsed_files)
            return True

        return False

    @staticmethod
    def __scan_cdlc_files_in_tmp():
        cdlc_files = file_utils.get_files_from_directory(TMP_DIR)

        if len(cdlc_files) > 0:
            log.error('Found %s CDLC files in %s directory (they were probably not parsed before). Files: %s',
                      len(cdlc_files), TMP_DIR_NAME, repr_in_multi_line(cdlc_files))

        return cdlc_files

    def __scan_cdlc_files_in_source_dirs(self):

        try:
            cdlc_files = file_utils.get_files_from_directories(self.source_directories)
        except BadDirectoryError as bde:
            log.error("---------------------------------------")
            log.error("Bad definition of the section FileManager of key source_directories!")
            log.error("Directory %s is bad or could not be reached, therefore it will be not checked anymore.",
                      format(bde.directory))
            log.error("Please fix the configuration!")
            log.error("---------------------------------------")
            self.source_directories.discard(bde.directory)
            return

        if len(cdlc_files) > 0:
            log.info('Found %s new CDLC file under source dirs.', len(cdlc_files))
            log.debug(cdlc_files)

        return cdlc_files

    def __scan_cdlc_files_in_destination_dir(self):
        return file_utils.get_not_parsed_files_from_directory(self.destination_directory)

    def __move_files_to_destination_dir(self, files):
        if files and len(files) > 0:
            file_utils.move_files_to(self.destination_directory, files)
