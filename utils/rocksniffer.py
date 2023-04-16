import json
from urllib.request import urlopen

from utils.exceptions import RocksnifferConnectionError


class Rocksniffer:
    def __init__(self, config_data):
        """
        Rocksniffer reader. Minimalistic, can be improved
        """
        self.enabled = config_data.sniffer.enabled
        self.host = config_data.sniffer.host
        self.port = config_data.sniffer.port

        self.memory = None

        self.artistName = None
        self.songName = None
        self.albumName = None
        self.songLength = None
        self.albumYear = None
        # TODO add last artist, song, etc. values? Needed?

        self.samples = [0, 0, 0]

    def update_config(self, config_data):
        self.enabled = config_data.sniffer.enabled
        self.host = config_data.sniffer.host
        self.port = config_data.sniffer.port

    def update(self):
        """
        Get the content of Rocksniffer. In case of success, take a sample of the song time
        """
        try:
            self.memory = self.get_sniffer_data()
            if self.memory["success"]:
                self.take_sample()
                self.get_song_details()
        except Exception:
            raise RocksnifferConnectionError(self.host, self.port)

    def get_sniffer_data(self):
        request = f"http://{self.host}:{self.port}/"
        with urlopen(request) as response:
            result = json.loads(response.read().decode(response.headers.get_content_charset('utf-8')))
        return result

    def get_song_details(self):
        self.artistName = self.memory['songDetails']['artistName']
        self.songName = self.memory['songDetails']['songName']
        self.albumName = self.memory['songDetails']['albumName']
        self.songLength = self.memory['songDetails']['songLength']
        self.albumYear = self.memory['songDetails']['albumYear']

    def take_sample(self):
        """
        Take a sample of the song time up to 3
        :return:
        """
        self.samples.append(self.memory['memoryReadout']['songTimer'])
        if len(self.samples) > 3:
            self.samples.pop(0)

    @property
    def success(self):
        try:
            return self.memory['success']
        except:
            return False

    @property
    def in_pause(self):
        """
        Logic for pause detection
        :return:
        """
        time_between_samples = abs(self.samples[0] - self.samples[2])
        if time_between_samples <= 2:
            return not self.samples[0] < self.samples[1] < self.samples[2]

        return True

    @property
    def current_state(self):
        return self.memory["currentState"]

    @property
    def in_game(self):
        return self.current_state in range(3, 5)
