import json

from dataclasses import dataclass
from urllib.request import urlopen

from utils.exceptions import RocksnifferConnectionError

@dataclass
class SongDetails:
    artist_name: str | None = None
    song_name: str | None = None
    album_name: str | None = None
    song_length: int | None = None
    album_year: int | None = None

class Rocksniffer:
    def __init__(self, config_data):
        """
        Rocksniffer reader. Minimalistic, can be improved
        """
        self.enabled = config_data.sniffer.enabled
        self.host = config_data.sniffer.host
        self.port = config_data.sniffer.port

        self.memory = None
        self.song_details = SongDetails()
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
        except Exception as e:
            raise RocksnifferConnectionError(self.host, self.port) from e

    def get_sniffer_data(self):
        request = f"http://{self.host}:{self.port}/"
        with urlopen(request) as response:
            result = json.loads(response.read().decode(response.headers.get_content_charset('utf-8')))
        return result

    def get_song_details(self):
        details = self.memory["songDetails"]

        self.song_details = SongDetails(
            artist_name=details["artistName"],
            song_name=details["songName"],
            album_name=details["albumName"],
            song_length=details["songLength"],
            album_year=details["albumYear"],
        )

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
        # Return False if no data is available or the success field is missing.
        return bool(self.memory and self.memory.get("success", False))

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

    @property
    def artist_name(self):
        return self.song_details.artist_name

    @property
    def song_name(self):
        return self.song_details.song_name

    @property
    def album_name(self):
        return self.song_details.album_name

    @property
    def song_length(self):
        return self.song_details.song_length

    @property
    def album_year(self):
        return self.song_details.album_year
