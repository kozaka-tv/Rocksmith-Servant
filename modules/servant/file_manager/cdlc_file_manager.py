import datetime
import logging
import math

from common.definitions import TMP_DIR
from utils import file_utils, collection_utils
from utils.collection_utils import repr_in_multi_line, is_collection_not_empty

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
            self.download_dirs: set = config_data.file_manager.download_dirs
            self.destination_dir = config_data.file_manager.destination_dir
            self.using_cfsm = config_data.file_manager.using_cfsm

    def update_config(self, config_data):
        self.enabled = config_data.file_manager.enabled
        self.download_dirs = config_data.file_manager.download_dirs
        self.destination_dir = config_data.file_manager.destination_dir
        self.using_cfsm = config_data.file_manager.using_cfsm

    def run(self):
        if self.enabled:
            if self.__beat_last_run_not_parsed():
                self.__move_non_parsed_files_to_tmp_dir()

            elif self.__beat_last_run():
                self.__move_files_to_destination_dir(self.__scan_cdlc_files_in_tmp())
                self.__move_files_to_destination_dir(self.__scan_cdlc_files_in_download_dirs())

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

        if is_collection_not_empty(non_parsed_files):
            log.warning(
                "Found %s file(s) in %s dir which one(s) were not yet parsed so I moving them to %s now! Files: %s"
                , len(non_parsed_files), self.destination_dir, TMP_DIR, repr_in_multi_line(non_parsed_files))
            file_utils.move_files_to(TMP_DIR, non_parsed_files)
            return True

        return False

    @staticmethod
    def __scan_cdlc_files_in_tmp():
        cdlc_files = file_utils.get_files_from_directory(TMP_DIR)

        if len(cdlc_files) > 0:
            log.error('Found %s CDLC files in %s directory (they were probably not parsed before). Files: %s',
                      len(cdlc_files), TMP_DIR, repr_in_multi_line(cdlc_files))

        return cdlc_files

    def __scan_cdlc_files_in_download_dirs(self) -> set:

        cdlc_files, bad_dirs = file_utils.get_files_from_directories(self.download_dirs)

        if collection_utils.is_collection_not_empty(bad_dirs):
            log.error("---------------------------------------")
            log.error('Bad definition or could not reach some directories defined in the config '
                      'under the section FileManager with the key download_dirs')
            log.error('Bad directories will be excluded from next search: %s', repr_in_multi_line(bad_dirs))
            log.error("---------------------------------------")
            for bad_dir in bad_dirs:
                self.download_dirs.discard(bad_dir)

        if len(cdlc_files) > 0:
            log.warning('Found %s new CDLC file under source dirs. Files:%s',
                        len(cdlc_files), repr_in_multi_line(cdlc_files))

        return cdlc_files

    def __scan_cdlc_files_in_destination_dir(self):
        return file_utils.get_not_parsed_files_from_directory(self.destination_dir)

    def __move_files_to_destination_dir(self, files):
        if files and len(files) > 0:
            file_utils.move_files_to(self.destination_dir, files)
