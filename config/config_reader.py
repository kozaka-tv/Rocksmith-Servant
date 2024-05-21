import configparser
import logging
import os
import sys

from config.config_ini_template import serialized
from utils import file_utils
from utils.string_utils import strtobool

ERROR_MSG = "Error retrieving value from %s for section [%s] with key [%s]."

log = logging.getLogger()


class ConfigTemplateError(Exception):
    def __init__(self, config_template_file, section, key):
        super().__init__(ERROR_MSG, config_template_file, section, key)


class ConfigReader:
    def __init__(self, config_file):
        self.config_template_file = "config_ini_template.py"

        self.config_file = config_file
        self.config_dirname = os.path.dirname(config_file)
        self.config_filename = os.path.basename(config_file)
        self.config_abspath = os.path.abspath(config_file)

        file_utils.create_directory_logged(self.config_dirname)

        log.warning('Initialising %s from %s ...', self.config_filename, self.config_dirname)

        self.last_modified = None

        # TODO remove content later and use variables only?
        self.content = self.load_content_from_config()

        self.if_needed_create_config_from_template_and_then_stop()

        self.log_config()

    def if_needed_create_config_from_template_and_then_stop(self):
        if self.last_modification_time == 0:
            self.save()
            log.error(
                'Because this is the first run, and no %s file was found, I created a configuration file for '
                'you from a template in: %s', self.config_filename, self.config_dirname)
            log.info(
                'Please change the values in the %s file according to your needs, and then relaunch Rocksmith Servant!',
                self.config_filename)
            log.warning('...press any key to exit this program.')
            input()
            sys.exit()

    def load_content_from_config(self):
        """
        Loads the default config and overwrites it with the config file
        :return: Config Object
        """
        config = self.get_default_config_ini()
        config.read(self.config_file, encoding="UTF-8")
        self.last_modified = self.last_modification_time

        if self.last_modified != 0:
            log.warning('%s has been loaded!', self.config_file)

        return config

    # TODO actually this should be used by all the modules to log config out. Config, Debug, Run.
    # TODO enhance with other values? Or make a debug part in the module itself? Would be better!
    def log_config(self):
        log.warning('------- CONFIG ------------------------------------------------')
        self.log_enabled_modules()
        log.warning('------- SOME IMPORTANT CONFIG VALUES --------------------------')

        log.info('RockSniffer.host = %s', str(self.get('RockSniffer', 'host')))
        log.info('RockSniffer.port = %s', str(self.get('RockSniffer', 'port')))

        log.info('SongLoader.cdlc_archive_dir = %s', str(self.get('SongLoader', 'cdlc_archive_dir')))
        log.info('SongLoader.rocksmith_cdlc_dir = %s', str(self.get('SongLoader', 'rocksmith_cdlc_dir')))
        log.info('SongLoader.allow_load_when_in_game = %s', str(self.get('SongLoader', 'allow_load_when_in_game')))

        log.warning('---------------------------------------------------------------')

    def log_enabled_modules(self):
        log.warning('--- Enabled Modules ---')
        self.log_module_if_enabled('RockSniffer')
        self.log_module_if_enabled('SetlistLogger')
        self.log_module_if_enabled('SongLoader')
        self.log_module_if_enabled('SceneSwitcher')
        self.log_module_if_enabled('FileManager')
        log.warning('---------------')

    def log_module_if_enabled(self, feature_name):
        if self.get_bool(feature_name, 'enabled'):
            log.warning(feature_name)

    def config_changed_and_reloaded(self):
        """
        Reload only if the config file has been changed
        :return: True if config file has been changed and reloaded, otherwise False
        """
        if self.last_modified != self.last_modification_time:
            self.content = self.load_content_from_config()
            return True

        return False

    def save(self):
        """
        Write the config to the specified path
        """
        with open(self.config_abspath, 'w', encoding="utf-8") as configfile:
            self.content.write(configfile)

    @property
    def last_modification_time(self):
        """ Return last modified time of the config """
        try:
            return os.stat(self.config_abspath).st_mtime
        except FileNotFoundError:
            return 0

    @staticmethod
    def get_default_config_ini():
        """
        get Config Object from the serialized default config
        :return:
        """
        config = configparser.ConfigParser()

        for section in serialized:
            config[section] = {}
            for key in serialized[section]:
                config[section][key] = str(serialized[section][key])

        return config

    def get_int_value(self, section, key) -> int:
        return self.get(section, key, int)

    def get_bool(self, section, key) -> bool:
        return self.get(section, key, bool)

    def get_list(self, section, key) -> list:
        return self.get(section, key, list)

    def get_set(self, section, key) -> set:
        return self.get(section, key, set)

    def get(self, section, key, cast=str):

        try:
            # List in config are separated with ";". Leading and trailing whitespaces will be removed
            if cast == list:
                return [v.strip() for v in self.content[section][key].split(";")]
            if cast == set:
                return set([v.strip() for v in self.content[section][key].split(";")])

            # Cast to bool
            if cast == bool:
                return strtobool(self.content[section][key].lower())

            # Else we cast it
            return cast(self.content[section][key])
        except:
            # To keep consistency and ease to use for the end user correct the bad value
            self.log_bad_value_message(section, key, cast)
            self.replace_bad_value(section, key, cast)
            return self.get(section, key, cast)

    def replace_bad_value(self, section, key, cast):
        # Get value from the template
        try:
            if cast == bool:
                new_key = str(serialized[section][key])
            else:
                new_key = serialized[section][key]
        except KeyError:
            raise ConfigTemplateError(self.config_template_file, section, key)

        # Replace and save the config value with a default value according to type
        self.content[section][key] = new_key
        self.save()

        log.warning("Bad value has been replaced with the default: %s", new_key)

    def log_bad_value_message(self, section, key, cast):
        log.error(ERROR_MSG, self.config_abspath, section, key)
        if cast == bool:
            log.info("For this type of key, please use either False, No, 0 or True, Yes, 1")

    def reload_if_changed(self):
        if self.config_changed_and_reloaded():
            log.warning("Configuration has been reloaded!")
            self.log_config()
            return True

        return False
