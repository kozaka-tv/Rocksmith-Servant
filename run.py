from time import sleep

import logger
from configReader import ConfigReader
# Initializing configuration
from debug import Debugger
from rocksniffer import Rocksniffer
from song_logger import SongLogger

conf = ConfigReader()

# Initializing main objects
# Init Rocksniffer values
sniffer = Rocksniffer(
    conf.get_value("RockSniffer", "host"),
    conf.get_value("RockSniffer", "port"),
)
# Init OBSWebSocket
# TODO
# Init Behaviour
# TODO
# Init debug
# TODO
# Init SongLogger values
song_logger = SongLogger(
    conf.get_value("SongLogger", "setlist_path"),
)
debugger = Debugger(
    conf.get_value("Debugging", "debug", int),
    conf.get_value("Debugging", "debug_log_interval", int)
)


# TODO extend with other values!
def update_config():
    # Updating Rocksniffer Configurations
    sniffer.host = conf.get_value("RockSniffer", "host")
    sniffer.port = conf.get_value("RockSniffer", "port")

    # Updating Debug Configurations
    debugger.debug = conf.get_value("Debugging", "debug", int)
    debugger.interval = conf.get_value("Debugging", "debug_log_interval", int)


# TODO move to debug Class?
def get_debug_message():
    sniffer_str = "{sniffer.artistName} - {sniffer.songName} " \
                  "({sniffer.albumYear}, {sniffer.albumName}), " \
                  "duration:{sniffer.songLength}s " \
                  "".format(sniffer=sniffer)
    debug_str = " | debug: {0} interval: {1}".format(str(debugger.debug), str(debugger.interval))
    setlist = " | setlist: {0}".format(str(song_logger.setlist));
    return sniffer_str + debug_str + setlist


def in_game():
    return sniffer.in_game and not sniffer.in_pause


def register_song_to_setlist():
    song_logger.log_a_song(sniffer.artistName + " - " + sniffer.songName)


def update_sniffer_internals():
    try:
        if not sniffer.memory:
            logger.notice("Starting sniffing..")
        sniffer.update()
        # return sniffer.success
    except ConnectionError:
        import traceback

        traceback.print_exc()
        sniffer.memory = None
        # return True


# Main loop
while True:
    # Sleep a bit
    sleep(0.1)

    if conf.reload_if_changed():
        update_config()

    # Updating Rocksniffer and if failed, restarting the loop till it is fixed
    update_sniffer_internals()
    if not sniffer.success:
        continue

    if in_game():
        register_song_to_setlist()

    # Interval debugging
    debugger.log_on_interval(get_debug_message())
