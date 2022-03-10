from time import time, sleep

from definitions import ROOT_DIR
from utils import logger, file_utils

MODULE_NAME = "FileManager"

HEARTBEAT = 10


class FileManager:
    def __init__(self, enabled, source_directories, destination_directory, using_cfsm):
        """
        File manager to manage CDLC files
        """
        self.enabled = enabled
        self.last_run = time()
        self.source_directories = source_directories
        self.destination_directory = destination_directory
        self.using_cfsm = using_cfsm

    def run(self):
        if self.enabled:
            if time() - self.last_run >= HEARTBEAT:
                self.move_not_parsed_files()

            files_to_move_in_source_dir = self.scan_cdlc_files_in_root()
            self.move_downloaded_cdlc_files(files_to_move_in_source_dir)

            files_to_move_in_source_dir = self.scan_cdlc_files_in_source_dirs()
            self.move_downloaded_cdlc_files(files_to_move_in_source_dir)

    def move_not_parsed_files(self):
        files_to_move_from_destination_dir = self.scan_cdlc_files_in_destination_dir()

        if len(files_to_move_from_destination_dir) > 0:
            self.move_not_enumerated_cdlc_files(files_to_move_from_destination_dir)
            # TODO use heartbeat (outside) maybe? Not a sleep?
            sleep(2)  # wait a bit

        self.last_run = time()

    @staticmethod
    def scan_cdlc_files_in_root():
        cdlc_files = file_utils.get_files_from_directory(ROOT_DIR)

        if len(cdlc_files) > 0:
            logger.log('Found {} new CDLC files in root.'.format(len(cdlc_files)), MODULE_NAME)
            logger.debug(cdlc_files)

        return cdlc_files

    def scan_cdlc_files_in_source_dirs(self):
        cdlc_files = file_utils.get_files_from_directories(self.source_directories)

        if len(cdlc_files) > 0:
            logger.log('Found {} new CDLC file under source dirs.'.format(len(cdlc_files)), MODULE_NAME)
            logger.debug(cdlc_files)

        return cdlc_files

    def scan_cdlc_files_in_destination_dir(self):
        cdlc_files = file_utils.get_not_parsed_files_from_directory(self.destination_directory)

        if len(cdlc_files) > 0:
            logger.log('Found {} not loaded CDLC files.'.format(len(cdlc_files)), MODULE_NAME)

        return cdlc_files

    @staticmethod
    def move_not_enumerated_cdlc_files(files):
        if len(files) > 0:
            file_utils.move_files(files, ROOT_DIR, MODULE_NAME)

    def move_downloaded_cdlc_files(self, files):
        if len(files) > 0:
            file_utils.move_files(files, self.destination_directory, MODULE_NAME)
