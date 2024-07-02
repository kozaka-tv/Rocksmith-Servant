from config.config_data import ConfigData
from modules.file_manager.cdlc_file_manager import FileManager
from modules.song_loader.song_loader import SongLoader
from utils.exceptions import ConfigError


def check_modules_enabled(config_data):
    check_that_is_any_module_enabled(config_data)
    # TODO call check_enabled_module_dependencies()


def check_that_is_any_module_enabled(config_data: ConfigData):
    # TODO use config_data.song_loader.enabled
    # TODO use a shortcut. If any is enabled, do not check the next, just return. None found, raise ConfigError

    # Search in all attributes that has "enabled" attribute
    modules_enabled = [getattr(getattr(config_data, attr), 'enabled', False) for attr in dir(config_data) if
                       not attr.startswith('__')]

    if not any(modules_enabled):
        raise ConfigError("!!! None of the modules are enabled !!!")


# TODO use config_data as input
def check_enabled_module_dependencies(song_loader: SongLoader, file_manager: FileManager):
    # TODO use config_data as input
    # TODO use config_data.song_loader.enabled
    # TODO Merge the logic into the check_that_is_any_module_enabled
    if song_loader.enabled and not file_manager.enabled:
        raise ConfigError("Please enable FileManager if you wanna use the SongLoader!")
