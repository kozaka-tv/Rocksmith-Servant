import datetime

import math

from definitions import ROOT_DIR
from utils import logger, file_utils

MODULE_NAME = "FileManager"

HEARTBEAT = 1
HEARTBEAT_NOT_PARSED = 5


class FileManager:
    def __init__(self, enabled, source_directories, destination_directory, using_cfsm):
        """
        File manager to manage CDLC files
        """
        self.enabled = enabled
        self.last_run = datetime.datetime.now()
        self.last_run_not_parsed = self.last_run
        self.source_directories = source_directories
        self.destination_directory = destination_directory
        self.using_cfsm = using_cfsm

    def run(self):
        if self.enabled:
            if self.beat_last_run_not_parsed():
                logger.debug("Scan and move not parsed files... ", MODULE_NAME)
                self.log_warning_times()
                moved = self.move_not_parsed_files()

                if moved:
                    logger.debug("Files were moved... ", MODULE_NAME)
                    self.log_warning_times()
                    self.last_run = datetime.datetime.now()
                    self.last_run_not_parsed = self.last_run
                    self.log_warning_times()
                else:
                    logger.debug("Nothing moved... ", MODULE_NAME)
                    self.log_warning_times()
                    self.last_run = datetime.datetime.now()
                    self.last_run_not_parsed = self.last_run
                    self.log_warning_times()

            elif self.beat_last_run():
                logger.debug("Scan and move files from root and source dirs...", MODULE_NAME)
                self.log_warning_times()

                files_to_move_in_source_dir = self.scan_cdlc_files_in_root()
                self.move_downloaded_cdlc_files(files_to_move_in_source_dir)

                files_to_move_in_source_dir = self.scan_cdlc_files_in_source_dirs()
                self.move_downloaded_cdlc_files(files_to_move_in_source_dir)

                self.last_run = datetime.datetime.now()

    def log_warning_times(self):
        logger.warning(
            "time()={} self.last_run={} self.last_run_not_parsed={}".format(
                datetime.datetime.now().second,
                self.last_run.second,
                self.last_run_not_parsed.second), MODULE_NAME)

    def beat_last_run(self):
        return math.floor((datetime.datetime.now() - self.last_run).seconds) >= HEARTBEAT

    def beat_last_run_not_parsed(self):
        return math.floor((datetime.datetime.now() - self.last_run_not_parsed).seconds) >= HEARTBEAT_NOT_PARSED

    def move_not_parsed_files(self):
        files_to_move_from_destination_dir = self.scan_cdlc_files_in_destination_dir()

        if len(files_to_move_from_destination_dir) > 0:
            logger.error("Found {} file(s) which one(s) were not parsed! files: {}".format(
                len(files_to_move_from_destination_dir), files_to_move_from_destination_dir), MODULE_NAME)
            self.move_not_enumerated_cdlc_files(files_to_move_from_destination_dir)
            return True

        return False

    @staticmethod
    def scan_cdlc_files_in_root():
        cdlc_files = file_utils.get_files_from_directory(ROOT_DIR)

        if len(cdlc_files) > 0:
            logger.log('Found {} CDLC files in root directory what is not parsed probably.'.format(len(cdlc_files)),
                       MODULE_NAME)
            logger.debug(cdlc_files, MODULE_NAME)

        return cdlc_files

    def scan_cdlc_files_in_source_dirs(self):
        cdlc_files = file_utils.get_files_from_directories(self.source_directories)

        if len(cdlc_files) > 0:
            logger.log('Found {} new CDLC file under source dirs.'.format(len(cdlc_files)), MODULE_NAME)
            logger.debug(cdlc_files, MODULE_NAME)

        return cdlc_files

    def scan_cdlc_files_in_destination_dir(self):
        return file_utils.get_not_parsed_files_from_directory(self.destination_directory)

    @staticmethod
    def move_not_enumerated_cdlc_files(files):
        if len(files) > 0:
            file_utils.move_files(files, ROOT_DIR, MODULE_NAME)

    def move_downloaded_cdlc_files(self, files):
        if len(files) > 0:
            file_utils.move_files(files, self.destination_directory, MODULE_NAME)
