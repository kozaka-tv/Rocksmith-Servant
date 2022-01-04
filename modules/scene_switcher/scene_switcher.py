from utils import logger


class SceneSwitcher:
    def __init__(self, enabled):
        """
        Scene Switcher
        :param enabled: Is the Module enabled?
        """
        self.enabled = enabled
        pass

    def run(self):
        if self.enabled:
            # TODO create main method and call it from here like other
            logger.notice("TODO Scene switcher!")
