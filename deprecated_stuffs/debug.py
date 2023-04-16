import logging
import time

log = logging.getLogger()


class Debugger:
    def __init__(self, config_data):
        self.debug = config_data.debugger.debug
        self.interval = config_data.debugger.interval

        self.last_log = 0

    def update_config(self, config_data):
        self.debug = config_data.debugger.debug
        self.interval = config_data.debugger.interval

    pass

    def log(self, message):
        if self.debug:
            log.debug("[DEBUG] %s", message)

    def log_on_interval(self, message):
        if self.last_log + self.interval < time.time():
            self.log(message)
            self.last_log = time.time()
