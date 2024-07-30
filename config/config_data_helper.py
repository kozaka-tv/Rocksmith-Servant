from config.config_data import ConfigData
from utils.exceptions import ConfigError


def check_modules_enabled(config_data: ConfigData):
    if not (config_data.sniffer.enabled or
            config_data.setlist_logger.enabled or
            config_data.file_manager.enabled or
            config_data.song_loader.enabled or
            config_data.scene_switcher.enabled):
        raise ConfigError("!!! None of the modules are enabled !!!")

    if config_data.song_loader.enabled and not config_data.file_manager.enabled:
        raise ConfigError("Please enable FileManager if you wanna use the SongLoader!")
