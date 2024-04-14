import datetime
import logging
import math

from definitions import TMP_DIR, TMP_DIR_NAME
from utils import file_utils
from utils.collection_utils import repr_in_multi_line
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
            if self.beat_last_run_not_parsed():
                log.debug("Scan and move not parsed files... ")
                moved = self.move_not_parsed_files_to_tmp()

                if moved:
                    log.debug("Files were moved... ")
                    self.last_run = datetime.datetime.now()
                    self.last_run_not_parsed = self.last_run
                else:
                    log.debug("Nothing moved... ")
                    self.last_run = datetime.datetime.now()
                    self.last_run_not_parsed = self.last_run

            elif self.beat_last_run():
                log.debug("Scan and move files from %s and source dirs...", TMP_DIR_NAME)
                self.move_downloaded_cdlc_files(self.scan_cdlc_files_in_tmp())
                self.move_downloaded_cdlc_files(self.scan_cdlc_files_in_source_dirs())

                self.last_run = datetime.datetime.now()

    def beat_last_run(self):
        return math.floor((datetime.datetime.now() - self.last_run).seconds) >= HEARTBEAT

    def beat_last_run_not_parsed(self):
        return math.floor((datetime.datetime.now() - self.last_run_not_parsed).seconds) >= HEARTBEAT_NOT_PARSED

    def move_not_parsed_files_to_tmp(self):
        not_enumerated_cdlc_files = self.scan_cdlc_files_in_destination_dir()

        if len(not_enumerated_cdlc_files) > 0:
            log.warning("Found %s file(s) which one(s) were not yet parsed so I moving them to tmp now! Files: %s"
                        , len(not_enumerated_cdlc_files), repr_in_multi_line(not_enumerated_cdlc_files))
            file_utils.move_files_to(TMP_DIR, not_enumerated_cdlc_files)
            return True

        return False

    @staticmethod
    def scan_cdlc_files_in_tmp():
        cdlc_files = file_utils.get_files_from_directory(TMP_DIR)

        if len(cdlc_files) > 0:
            log.info('Found %s CDLC files in %s directory what is not parsed probably.', len(cdlc_files), TMP_DIR_NAME)
            log.debug("%s", cdlc_files)

        return cdlc_files

    def scan_cdlc_files_in_source_dirs(self):

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

    def scan_cdlc_files_in_destination_dir(self):
        return file_utils.get_not_parsed_files_from_directory(self.destination_directory)

    def move_downloaded_cdlc_files(self, files):
        if files and len(files) > 0:
            file_utils.move_files_to(self.destination_directory, files)
