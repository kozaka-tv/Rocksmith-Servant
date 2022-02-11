from time import sleep

from definitions import ROOT_DIR
from utils import logger, file_utils

MODULE_NAME = "FileManager"


class FileManager:
    def __init__(self, enabled, source_directories, destination_directory, using_cfsm):
        """
        File manager to manage CDLC files
        """
        self.enabled = enabled
        self.source_directories = source_directories
        self.destination_directory = destination_directory
        self.using_cfsm = using_cfsm

    def run(self):
        if self.enabled:
            files_to_move_from_destination_dir = self.scan_cdlc_files_in_destination_dir()
            self.move_not_enumerated_cdlc_files(files_to_move_from_destination_dir)
            sleep(5)  # TODO remove
            files_to_move_in_source_dir = self.scan_cdlc_files_in_root()
            self.move_downloaded_cdlc_files(files_to_move_in_source_dir)
            sleep(5)  # TODO remove
            files_to_move_in_source_dir = self.scan_cdlc_files_in_source_dirs()
            self.move_downloaded_cdlc_files(files_to_move_in_source_dir)
            sleep(5)  # TODO remove

    @staticmethod
    def scan_cdlc_files_in_root():
        cdlc_files = file_utils.get_files_from_directory(ROOT_DIR, MODULE_NAME, file_utils.CDLC_FILE_EXT)

        if len(cdlc_files) > 0:
            logger.log('Found {} new CDLC files in root.'.format(len(cdlc_files)), MODULE_NAME)

        return cdlc_files

    def scan_cdlc_files_in_source_dirs(self):
        cdlc_files = file_utils.get_files_from_directories(self.source_directories, MODULE_NAME,
                                                           file_utils.CDLC_FILE_EXT)

        if len(cdlc_files) > 0:
            logger.log('Found {} new CDLC files.'.format(len(cdlc_files)), MODULE_NAME)

        return cdlc_files

    def scan_cdlc_files_in_destination_dir(self):
        cdlc_files = file_utils.get_not_parsed_files_from_directory(self.destination_directory, MODULE_NAME,
                                                                    file_utils.CDLC_FILE_EXT)

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
