from time import sleep

import log

from debug import Debugger
from iniReader import INIReader

# Initializing main objects
# Configuration
conf = None
try:
    conf = INIReader("config.ini")
except FileNotFoundError:
    # log.notice('A config.ini file was created. Fill it, then relaunch Rocksmith Servant!')
    log.notice('Press any key to exit this program.')
    input()
    exit(0)




def get_debug_message():
    return "TODO - SOME DEBUG MESSAGE HERE"


# Init debug
debug = Debugger(
    conf.get_value("Debugging", "debug", int),
    conf.get_value("Debugging", "log_state_interval", int)
)
debug.log("Init Debug.")
# debug.log("[Behaviour]")
# for k, v in conf.content["Behaviour"].items():
#     debug.log("{} = {}".format(k, v))


def method_name():
    debug.debug = conf.get_value("Debugging", "debug", int)
    debug.interval = conf.get_value("Debugging", "log_state_interval", int)


# Main loop
while True:
    # Sleep and Reload the config.
    sleep(0.1)

    if conf.reload():
        log.notice("Configuration will be reloaded!")

        # Updating configuration
        method_name()

        log.notice("Configuration has been reloaded!")

    # Interval debugging
    debug.log_on_interval(get_debug_message())
