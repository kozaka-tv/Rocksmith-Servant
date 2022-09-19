import datetime

import math

from definitions import ROOT_DIR
from utils import logger, file_utils
from utils.exceptions import BadDirectoryError

MODULE_NAME = "FileManager"

HEARTBEAT = 1
HEARTBEAT_NOT_PARSED = 5

NON_PARSED_FILE_AGE_SECONDS = 9


class FileManager:
    def __init__(self, config_data):
        """
        File manager to manage CDLC files
        """
        self.enabled = config_data.file_manager.enabled
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
                logger.debug("Scan and move not parsed files... ", MODULE_NAME)
                moved = self.move_not_parsed_files()

                if moved:
                    logger.debug("Files were moved... ", MODULE_NAME)
                    self.last_run = datetime.datetime.now()
                    self.last_run_not_parsed = self.last_run
                else:
                    logger.debug("Nothing moved... ", MODULE_NAME)
                    self.last_run = datetime.datetime.now()
                    self.last_run_not_parsed = self.last_run

            elif self.beat_last_run():
                logger.debug("Scan and move files from root and source dirs...", MODULE_NAME)
                self.move_downloaded_cdlc_files(self.scan_cdlc_files_in_root())
                self.move_downloaded_cdlc_files(self.scan_cdlc_files_in_source_dirs())

                self.last_run = datetime.datetime.now()

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

        try:
            cdlc_files = file_utils.get_files_from_directories(self.source_directories)
        except BadDirectoryError as bde:
            logger.error("---------------------------------------", MODULE_NAME)
            logger.error("Bad definition of the section FileManager of key source_directories!", MODULE_NAME)
            logger.error("Directory {} is bad or could not be reached, "
                         "therefore it will be not checked anymore.".format(bde.directory), MODULE_NAME)
            logger.error("Please fix the configuration!", MODULE_NAME)
            logger.error("---------------------------------------", MODULE_NAME)
            self.source_directories.discard(bde.directory)
            return

        if len(cdlc_files) > 0:
            logger.log('Found {} new CDLC file under source dirs.'.format(len(cdlc_files)), MODULE_NAME)
            logger.debug(cdlc_files, MODULE_NAME)

        return cdlc_files

    def scan_cdlc_files_in_destination_dir(self):
        return file_utils.get_not_parsed_files_from_directory(self.destination_directory, NON_PARSED_FILE_AGE_SECONDS)

    @staticmethod
    def move_not_enumerated_cdlc_files(files):
        if len(files) > 0:
            file_utils.move_files(files, ROOT_DIR, MODULE_NAME)

    def move_downloaded_cdlc_files(self, files):
        if files and len(files) > 0:
            file_utils.move_files(files, self.destination_directory, MODULE_NAME)
