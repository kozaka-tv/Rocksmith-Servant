import configparser
import os
import sys
from distutils import util

import logger
from config.config_ini_template import serialized

PATH_CONFIG = os.path.join(os.path.dirname(__file__), "config.ini")


class ConfigReader:
    def __init__(self):

        logger.notice('Initialising ' + PATH_CONFIG + ' ...')

        # TODO remove content later and use variables only?
        self.content = self.load()
        self.log_config()

        self.last_modified = self.last_modification_time
        if self.last_modification_time == 0:
            self.save()
            logger.notice('A config.ini file was created for you from a template in: ' + PATH_CONFIG)
            logger.notice('Please change the values according to your needs, and then relaunch Rocksmith Servant!')
            logger.notice('...now please press any key to exit this program.')
            input()
            sys.exit()

    def load(self):
        """
        Loads the default config and overwrites it with the config file
        :return: Config Object
        """
        config = self.get_default_config_ini()
        config.read(PATH_CONFIG, encoding="UTF-8")
        self.last_modified = self.last_modification_time

        logger.notice(PATH_CONFIG + ' has been loaded!')

        return config

    # TODO actually this should be used by all the modules to log config out. Config, Debug, Run.
    def log_config(self):
        logger.notice('------- CONFIG ------------------------------------------------')
        self.log_enabled_modules()
        logger.notice('RockSniffer.host=' + str(self.get_str_value('RockSniffer', 'host')))
        logger.notice('RockSniffer.port=' + str(self.get_str_value('RockSniffer', 'port')))
        logger.notice('Debugging.debug=' + str(self.get_bool_value('Debugging', 'debug')))
        logger.notice('Debugging.debug_log_interval=' + str(self.get_int_value('Debugging', 'debug_log_interval')))
        logger.notice('---------------------------------------------------------------')

    def log_enabled_modules(self):
        logger.notice('--- Enabled Modules ---')
        self.log_module_if_enabled('RockSniffer')
        self.log_module_if_enabled('SetlistLogger')
        self.log_module_if_enabled('SongLoader')
        self.log_module_if_enabled('SceneSwitcher')
        logger.notice('---------------')

    def log_module_if_enabled(self, feature_name):
        if self.get_bool_value(feature_name, 'enabled'):
            logger.notice(feature_name)

    def reload(self):
        """
        Reload only if the config file has been changed
        :return: True if config file has been changed and it is reloaded else False
        """

        if self.last_modification_time == self.last_modified:
            return False
        else:
            self.content = self.load()
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

    def get_int_value(self, section, key):
        return self.get_value(section, key, int)

    def get_str_value(self, section, key):
        return self.get_value(section, key, str)

    def get_bool_value(self, section, key):
        return self.get_value(section, key, bool)

    # TODO this should be not available to call!
    def get_value(self, section, key, cast=str):

        try:
            # List in config are separated with ";". Leading and trailing whitespaces will be removed
            if cast == list:
                value = [v.strip() for v in self.content[section][key].split(";")]
            # Cast to bool
            if cast == bool:
                # value = self.content[section][key].lower() in ['true', '1', 't', 'y', 'yes']
                value = bool(util.strtobool(self.content[section][key].lower()))
            # Else we cast it
            else:
                value = cast(self.content[section][key])
            return value
        except:
            # To keep consistency and ease to use for the end user
            # Logging where the value was expected.
            # Replacing it to be sure it's still working even after this error.
            logger.notice("Error retrieving value for {} [{}][{}].".format(PATH_CONFIG, section, key, ))
            # Getting the new value
            key_ = serialized[section][key]
            logger.notice("Replacing value with : {}".format(key_))
            # Replacing the config value with a default value
            self.content[section][key] = serialized[section][key]
            # Saving the current INI to keep it safe to use
            self.save()
            # Returning new value, using this method
            return self.get_value(section, key, cast)

    def reload_if_changed(self):
        if self.reload():
            logger.notice("Configuration has been changed, so it is reloaded!")
            self.log_config()
            return True
        else:
            return False
