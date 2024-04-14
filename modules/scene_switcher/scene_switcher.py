import logging

log = logging.getLogger()


class SceneSwitcher:
    def __init__(self, config_data):
        """
        Scene Switcher
        """
        self.enabled = config_data.scene_switcher.enabled
        if self.enabled:
            log.warning("TODO Scene switcher!")

    def update_config(self, config_data):
        self.enabled = config_data.scene_switcher.enabled

    def run(self):
        if self.enabled:
            # TODO create main method and call it from here like other
            log.warning("TODO Scene switcher!")
