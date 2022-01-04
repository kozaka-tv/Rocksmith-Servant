import os
from time import sleep

from config.configReader import ConfigReader
from modules.scene_switcher.scene_switcher import SceneSwitcher
from modules.setlist.setlist_logger import SetlistLogger
from modules.song_loader.song_loader import SongLoader
from utils import logger
from utils.debug import Debugger
from utils.rocksniffer import Rocksniffer, RocksnifferConnectionError

# Initializing configuration
conf = ConfigReader()

# Initializing Modules
sniffer = Rocksniffer(
    # TODO is this enabled disabled needed? Or it should work with other modules together. Like Setlist will not work
    # without sniffer, etc.
    conf.get_bool_value("RockSniffer", "enabled"),
    conf.get_value("RockSniffer", "host"),
    conf.get_value("RockSniffer", "port"),
)
setlist_logger = SetlistLogger(
    conf.get_bool_value("SetlistLogger", "enabled"),
    conf.get_value("SetlistLogger", "setlist_path"),
)
song_loader = SongLoader(
    conf.get_bool_value("SongLoader", "enabled"),
    # TODO
    # conf.get_value("SetlistLogger", "setlist_path"),
)
scene_switcher = SceneSwitcher(
    conf.get_bool_value("SceneSwitcher", "enabled"),
)

# Initializing Debugger
debugger = Debugger(
    conf.get_bool_value("Debugging", "debug"),
    conf.get_value("Debugging", "debug_log_interval", int)
)


# TODO extend with other values!
# TODO can not this be in the Module itself?
def update_config():
    if conf.reload_if_changed():
        # Updating Rocksniffer Configurations
        sniffer.enabled = conf.get_bool_value("RockSniffer", "enabled")
        sniffer.host = conf.get_value("RockSniffer", "host")
        sniffer.port = conf.get_value("RockSniffer", "port")

        # Updating Setlist Configurations
        setlist_logger.enabled = conf.get_bool_value("SetlistLogger", "enabled")

        # Updating Song Loader Configurations
        song_loader.enabled = conf.get_bool_value("SongLoader", "enabled")
        # song_loader.setlist_path =  conf.get_value("SetlistLogger", "setlist_path")

        # TODO file

        # Updating Scene Switcher Configurations
        scene_switcher.enabled = conf.get_bool_value("SceneSwitcher", "enabled")

        # Updating Debug Configurations
        debugger.debug = conf.get_bool_value("Debugging", "debug")
        debugger.interval = conf.get_int_value("Debugging", "debug_log_interval")


# TODO move to debug Class?
def get_debug_message():
    # TODO
    # "SceneSwitcher: {sniffer.enabled}" \
    modules_str = "--- Modules ---" + os.linesep + \
                  "RockSniffer: {sniffer.enabled}" + os.linesep + \
                  "SetlistLogger: {setlist_logger.enabled}" + os.linesep + \
                  "SongLoader: {song_loader.enabled}" + os.linesep + \
                  "".format(sniffer=sniffer, setlist_logger=setlist_logger, song_loader=song_loader) + os.linesep + \
                  "---------------" + os.linesep

    sniffer_str = "Song: {sniffer.artistName} - {sniffer.songName} " \
                  "({sniffer.albumYear}, {sniffer.albumName}), " \
                  "duration:{sniffer.songLength}s " \
                  "".format(sniffer=sniffer) + os.linesep

    debug_str = "Debug: {0} interval: {1}".format(str(debugger.debug), str(debugger.interval)) + os.linesep

    setlist = "Setlist: {0}".format(str(setlist_logger.setlist)) + os.linesep

    return os.linesep + modules_str + sniffer_str + debug_str + setlist


def in_game():
    return sniffer.enabled and sniffer.in_game and not sniffer.in_pause


def put_the_song_into_the_setlist():
    if setlist_logger.enabled and in_game():
        setlist_logger.log_a_song(sniffer.artistName + " - " + sniffer.songName)


# TODO rename
def update_game_information():
    if sniffer.enabled:
        try:
            if not sniffer.memory or sniffer.memory is None:
                logger.notice("Try to connect to RockSniffer to get the information from Rocksmith...")
            sniffer.update()
        except RocksnifferConnectionError as rce:
            sniffer.memory = None
            raise rce


# Main loop
while True:
    #
    try:
        # Sleep a bit
        sleep(0.1)

        update_config()

        update_game_information()
        put_the_song_into_the_setlist()
        song_loader.load()
        scene_switcher.run()

        # Interval debugging
        debugger.log_on_interval(get_debug_message())

    # Catch and log all the known exceptions, but keep app alive.
    except RocksnifferConnectionError as error:
        logger.warning(error)
