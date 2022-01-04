import fnmatch
import os
import shutil

from utils import logger

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

        logger.warning("FileManager is initialised!")

    def run(self):
        if self.enabled:
            self.move_cdlc_files(self.scan_cdlc_files_in_source_dirs())

    def scan_cdlc_files_in_source_dirs(self):
        cdlc_files = []

        for source in self.source_directories:
            for root, dir_names, filenames in os.walk(source):
                for filename in fnmatch.filter(filenames, '*.psarc'):
                    file = os.path.join(root, filename)
                    cdlc_files.append(file)
                    logger.log('Found a new CDLC file to parse: {}'.format(file), MODULE_NAME)

        if len(cdlc_files) > 0:
            logger.log('Found {} new CDLC files.'.format(len(cdlc_files)), MODULE_NAME)

        return cdlc_files

    def move_cdlc_files(self, cdlc_files):
        if len(cdlc_files) > 0:
            logger.log('Moving {} CLDC files to: {}'.format(len(cdlc_files), self.destination_directory), MODULE_NAME)
            for file in cdlc_files:
                shutil.move(file, self.destination_directory)
