from time import sleep

import log

from debug import Debugger
from iniReader import INIReader
from rocksniffer import Rocksniffer
from song_logger import SongLogger

# Initializing main objects
# Configuration
conf = None
try:
    conf = INIReader("config.ini")
except FileNotFoundError:
    # TODO
    # log.notice('A config.ini file was created. Fill it, then relaunch Rocksmith Servant!')
    log.notice('Press any key to exit this program.')
    input()
    exit(0)

# Init debug
debug = Debugger(
    conf.get_value("Debugging", "debug", int),
    conf.get_value("Debugging", "log_state_interval", int)
)
# Init Rocksniffer values
sniffer = Rocksniffer(
    conf.get_value("RockSniffer", "host"),
    conf.get_value("RockSniffer", "port"),
)
# Init SongLogger values
song_logger = SongLogger(
    conf.get_value("SongLogger", "log_file_path"),
)


def get_debug_message():
    return "{sniffer.artistName} - {sniffer.songName} " \
           "({sniffer.albumYear}, {sniffer.albumName}), " \
           "duration:{sniffer.songLength}s " \
           "".format(sniffer=sniffer)


debug.log("Init Debug.")


def update_config():
    # Updating Rocksniffer Configurations
    sniffer.host = conf.get_value("RockSniffer", "host")
    sniffer.port = conf.get_value("RockSniffer", "port")

    # Updating Debug Configurations
    debug.debug = conf.get_value("Debugging", "debug", int)
    debug.interval = conf.get_value("Debugging", "log_state_interval", int)


def check_config_and_reload_if_changed():
    if conf.reload():
        log.notice("Configuration has been changed, so it will be reloaded!")

        # Updating configuration
        update_config()

        log.notice("Configuration has been reloaded!")


def in_game():
    return sniffer.in_game and not sniffer.in_pause


def register_song_to_setlist():
    song_logger.log_a_song(sniffer.artistName + " - " + sniffer.songName)


# Main loop
while True:
    # Sleep a bit
    sleep(0.1)

    check_config_and_reload_if_changed()

    # Updating Rocksniffer internal Values
    try:
        if not sniffer.memory:
            log.notice("Starting sniffing..")
        sniffer.update()
    except ConnectionError:
        import traceback

        traceback.print_exc()
        sniffer.memory = None
        log.notice("Updating Rocksniffer internal Values failed!")
        continue

    # If sniff failed explicitly, restarting the loop
    if not sniffer.success:
        continue

    # Interval debugging
    debug.log_on_interval(get_debug_message())

    # Main Logic
    # Case in game
    if in_game():
        register_song_to_setlist()
