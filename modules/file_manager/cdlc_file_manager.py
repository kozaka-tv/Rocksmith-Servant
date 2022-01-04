import fnmatch
import os
from time import sleep

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

        logger.notice("FileManager is initialised!")

    def run(self):
        if self.enabled:
            # TODO remove log and sleep later
            sleep(1)

            cdlc_files = []
            for source in self.source_directories:
                for root, dir_names, filenames in os.walk(source):
                    for filename in fnmatch.filter(filenames, '*.psarc'):
                        file = os.path.join(root, filename)
                        cdlc_files.append(file)
                        logger.discrete('Found a new CDLC file: {}'.format(file), MODULE_NAME)
            logger.notice('Found {} new CDLC files!'.format(len(cdlc_files)), MODULE_NAME)
