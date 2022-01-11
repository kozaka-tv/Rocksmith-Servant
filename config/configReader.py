import configparser
import os
import sys
from distutils import util

from config.config_ini_template import serialized
from utils import logger

CONFIG_FILE_NAME = "config.ini"
PATH_CONFIG = os.path.join(os.path.dirname(__file__), CONFIG_FILE_NAME)
PATH_CONFIG_TEMPLATE = os.path.join(os.path.dirname(__file__), "config_ini_template.py")

ERROR_MSG = "Error retrieving value from {} for section [{}] with key [{}]."


class ConfigTemplateError(Exception):
    def __init__(self, section, key):
        super().__init__(ERROR_MSG.format(PATH_CONFIG_TEMPLATE, section, key))


class ConfigReader:
    def __init__(self):

        logger.warning('Initialising ' + CONFIG_FILE_NAME + ' from ' + PATH_CONFIG + ' ...')

        self.last_modified = None

        # TODO remove content later and use variables only?
        self.content = self.load_content_from_config()

        self.create_config_from_template_if_not_exists_and_stop()

        self.log_config()

    def create_config_from_template_if_not_exists_and_stop(self):
        if self.last_modification_time == 0:
            self.save()
            logger.error('Because this is the first run, and no ' + CONFIG_FILE_NAME +
                         ' file was found, I created a configuration file for you from a template in: ' + PATH_CONFIG)
            logger.log('Please change the values in the ' + CONFIG_FILE_NAME +
                       ' file according to your needs, and then relaunch Rocksmith Servant!')
            logger.warning('...press any key to exit this program.')
            input()
            sys.exit()

    def load_content_from_config(self):
        """
        Loads the default config and overwrites it with the config file
        :return: Config Object
        """
        config = self.get_default_config_ini()
        config.read(PATH_CONFIG, encoding="UTF-8")
        self.last_modified = self.last_modification_time

        if self.last_modified != 0:
            logger.warning(PATH_CONFIG + ' has been loaded!')

        return config

    # TODO actually this should be used by all the modules to log config out. Config, Debug, Run.
    # TODO enhance with other values? Or mage a debug part in the module itself? Would be better!
    def log_config(self):
        logger.warning('')
        logger.warning('------- CONFIG ------------------------------------------------')
        self.log_enabled_modules()
        logger.warning('------- SOME IMPORTANT CONFIG VALUES --------------------------')

        logger.log('RockSniffer.host = ' + str(self.get('RockSniffer', 'host')))
        logger.log('RockSniffer.port = ' + str(self.get('RockSniffer', 'port')))

        logger.log('SongLoader.cfsm_file_name = ' + str(self.get('SongLoader', 'cfsm_file_name')))
        logger.log('SongLoader.allow_load_when_in_game = ' + str(self.get('SongLoader', 'allow_load_when_in_game')))

        logger.log('Debugging.debug = ' + str(self.get_bool('Debugging', 'debug')))
        logger.log('Debugging.debug_log_interval = ' + str(self.get_int_value('Debugging', 'debug_log_interval')))

        logger.warning('---------------------------------------------------------------')
        logger.warning('')

    def log_enabled_modules(self):
        logger.error('--- Enabled Modules ---')
        self.log_module_if_enabled('RockSniffer')
        self.log_module_if_enabled('SetlistLogger')
        self.log_module_if_enabled('SongLoader')
        self.log_module_if_enabled('SceneSwitcher')
        self.log_module_if_enabled('FileManager')
        logger.error('---------------')

    def log_module_if_enabled(self, feature_name):
        if self.get_bool(feature_name, 'enabled'):
            logger.warning(feature_name)

    def config_changed_and_reloaded(self):
        """
        Reload only if the config file has been changed
        :return: True if config file has been changed and it is reloaded else False
        """
        if self.last_modified == self.last_modification_time:
            return False
        else:
            self.content = self.load_content_from_config()
            return True

    def save(self):
        """
        Write the config to the specified path
        """
        with open(PATH_CONFIG, 'w') as configfile:
            self.content.write(configfile)

    @property
    def last_modification_time(self):
        """ Return last modified time of the config """
        try:
            return os.stat(PATH_CONFIG).st_mtime
        except FileNotFoundError:
            return 0

    def get_default_config_ini(self):
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

    def get(self, section, key, cast=str):

        try:
            # List in config are separated with ";". Leading and trailing whitespaces will be removed
            if cast == list:
                return [v.strip() for v in self.content[section][key].split(";")]

            # Cast to bool
            if cast == bool:
                return util.strtobool(self.content[section][key].lower())

            # Else we cast it
            else:
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
            raise ConfigTemplateError(section, key)

        # Replace and save the config value with a default value according to type
        self.content[section][key] = new_key
        self.save()

        logger.warning("Bad value has been replaced with the default: {}".format(new_key))

    @staticmethod
    def log_bad_value_message(section, key, cast):
        logger.error(ERROR_MSG.format(PATH_CONFIG, section, key))
        if cast == bool:
            logger.log("For this type of key, please use either False, No, 0 or True, Yes, 1")

    def reload_if_changed(self):
        if self.config_changed_and_reloaded():
            logger.warning("Configuration has been reloaded!")
            self.log_config()
            return True
        else:
            return False
