from utils import logger


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
            # TODO create main method and call it from here like other
            logger.notice("TODO FileManager!")
            pass
        pass
