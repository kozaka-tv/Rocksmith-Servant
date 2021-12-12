import os
from time import sleep

import logger
from configReader import ConfigReader
from debug import Debugger
from rocksniffer import Rocksniffer
from scene_switcher import SceneSwitcher
from setlist_logger import SetlistLogger
from song_loader import SongLoader

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
    # TODO
)

# Initializing Debugger
debugger = Debugger(
    conf.get_bool_value("Debugging", "debug"),
    conf.get_value("Debugging", "debug_log_interval", int)
)


# TODO extend with other values!
# TODO can not this be in the Module itself?
def update_config():
    # Updating Modules Configurations
    sniffer.enabled = conf.get_bool_value("RockSniffer", "enabled")
    setlist_logger.enabled = conf.get_bool_value("RockSniffer", "enabled")
    sniffer.enabled = conf.get_bool_value("RockSniffer", "enabled")
    sniffer.enabled = conf.get_bool_value("RockSniffer", "enabled")

    # Updating Rocksniffer Configurations
    sniffer.host = conf.get_value("RockSniffer", "host")
    sniffer.port = conf.get_value("RockSniffer", "port")

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
    return sniffer.in_game and not sniffer.in_pause


def register_song_to_setlist():
    setlist_logger.log_a_song(sniffer.artistName + " - " + sniffer.songName)


def update_sniffer_internals():
    try:
        if not sniffer.memory:
            logger.notice("Try update Sniffer...")
        sniffer.update()
    except ConnectionError:
        import traceback

        logger.warning("Connection problem to Rocksniffer!")
        logger.warning(traceback.format_exc())
        sniffer.memory = None


# Main loop
while True:
    #
    try:
        # Sleep a bit
        sleep(0.1)

        if conf.reload_if_changed():
            update_config()

        if sniffer.enabled:
            # Updating Rocksniffer and if failed, restarting the loop till it is fixed
            update_sniffer_internals()
            # TODO needed? It could be that we do not use Sniffer!
            # if not sniffer.success:
            #     continue

        # if in game, try to register a new song to the setlist if not already added
        if setlist_logger.enabled and in_game():
            register_song_to_setlist()

        if song_loader.enabled and sniffer.enabled:
            # TODO or maybe this should be configurable?
            # else:  # load songs only in case we are not in game to avoid lagg in game
            song_loader.load()

        if scene_switcher.enabled:
            # TODO
            pass

        # Interval debugging
        debugger.log_on_interval(get_debug_message())

    # Catch all the type of known exceptions, but keep app alive.
    except (TypeError, ConnectionError):
        import traceback

        logger.warning("Error in main logic!")
        logger.warning(traceback.format_exc())
