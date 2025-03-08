import logging

from dacite import from_dict

from config.config_data import ConfigData
from modules.servant.song_loader.dataclasses.rs_playlist_data import RsPlaylist
from modules.servant.song_loader.song_loader import SongLoader
from utils.rs_playlist_util import get_playlist

log = logging.getLogger()


class TagManager:
    def __init__(self, config_data: ConfigData, song_loader: SongLoader):
        # TODO
        # TODO
        # TODO
        rsplaylist = self.get_rsplaylist(config_data)
        self.all_tags = self.__fetch_all_tags(rsplaylist)
        self.user_tags = self.__fetch_user_tags(rsplaylist)
        self.server_tags = self.__fetch_server_tags(rsplaylist)

    @staticmethod
    def get_rsplaylist(config_data):
        loader = config_data.song_loader
        new_playlist = get_playlist(loader.twitch_channel, loader.phpsessid)
        rsplaylist = from_dict(data_class=RsPlaylist, data=new_playlist)
        return rsplaylist

    @staticmethod
    def __fetch_all_tags(rsplaylist):
        return {value.name: key for key, value in rsplaylist.channel_tags.items()}

    @staticmethod
    def __fetch_server_tags(rsplaylist):
        return {value.name: key for key, value in rsplaylist.channel_tags.items() if not value.user}

    @staticmethod
    def __fetch_user_tags(rsplaylist):
        return {value.name: key for key, value in rsplaylist.channel_tags.items() if value.user}

    # def update_tags(self, new_playlist):
    #     self.rsplaylist_json = new_playlist
    #     self.rsplaylist = from_dict(data_class=RsPlaylist, data=new_playlist)
    #
    # def __log_available_rspl_tags(self):
    #     tags = self.rsplaylist.channel_tags
    #     user_tags = {value.name: key for key, value in tags.items() if value.user}
    #     log.warning("Tags set in RSPlaylist:\n%s", pprint.pformat(user_tags))
