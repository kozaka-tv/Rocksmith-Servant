import os
import pathlib
import sqlite3
from time import sleep

import requests

from utils import logger, file_utils

MODULE_NAME = "SongLoader"
CDLC_DIR = '../../import'
DEFAULT_CFSM_FILE_NAME = '../../temp/temp_song_loader/SongsMasterGrid.json'

con = sqlite3.connect('./servant.db')


class SongLoader:
    def __init__(self, enabled, cdlc_dir='import', cfsm_file_name=DEFAULT_CFSM_FILE_NAME,
                 allow_load_when_in_game=True):
        self.enabled = enabled
        self.cdlc_dir = os.path.join(cdlc_dir)
        self.cfsm_file_name = cfsm_file_name
        self.songs_to_load = os.path.join(cdlc_dir, cfsm_file_name)
        self.allow_load_when_in_game = allow_load_when_in_game

        self.first_run = True

        # TODO maybe call this different...do we need this?
        self.raw_playlist = None

        # TODO this should be maybe in run or in config reader?
        self.create_cdlc_directory()

    # @staticmethod
    def create_cdlc_directory(self):
        if self.enabled:
            # self.cdlc_dir = os.path.join(CDLC_DIR)
            logger.warning("Creating cdlc directory to: {}".format(self.cdlc_dir))
            pathlib.Path(self.cdlc_dir).mkdir(parents=True, exist_ok=True)

    def load(self):
        if self.enabled:
            # TODO remove this log
            logger.warning("---------------------- ")
            logger.warning("Song Loader is running... ")

            if self.first_run:
                logger.log("Try to load new songs for the CFSM file: {}".format(self.songs_to_load))
                self.first_run = False

            self.get_file_to_import()

            # pass
            # TODO or maybe this should be configurable?
            # else:  # load songs only in case we are not in game to avoid lagging in game
            self.get_playlist()

            # TODO remove this sleep
            sleep(3)

    def get_file_to_import(self):
        path = file_utils.get_file_path(self.cdlc_dir, self.cfsm_file_name)
        logger.log('CFSM_file to load: {}'.format(path), MODULE_NAME)

    def get_playlist(self):
        # TODO sleep to avoid too much requests
        # sleep(3)

        rs_playlist_url = "https://rsplaylist.com/ajax/playlist.php?channel=kozaka"
        # TODO get the PHPSESSID from config!
        cookies = {'PHPSESSID': '4hsjtoq26pvtavh062jdsplfp8'}

        playlist = requests.get(rs_playlist_url, cookies=cookies).json()
        # logger.log(playlist)

        for sr in playlist["playlist"]:
            logger.log("---- sr " + str(sr["position"]) + " -------")
            for cdlc in sr["dlc_set"]:
                id_ = cdlc["id"]
                cdlc_id = cdlc["cdlc_id"]
                artist = cdlc["artist"]
                title = cdlc["title"]
                logger.log(str(id_) + " - " + str(cdlc_id) + " - " + artist + " - " + title)

                # urlopen = requests.get(rs_playlist_url)
                # text = urlopen.text
                # data2 = json.loads(text)
                # for data2entry in data2["playlist"]:
                #     logger.log(data2entry)
                #     set_ = data2entry["dlc_set"]
                #     logger.log(set_)

                # response = requests.get(rs_playlist_url)
                # response_json = response.json()
                # datazzz = json.loads(response_json)
                # playlist_0 = r_json['playlist']
                # extracted = extract_values(r_json, 'dlc_set')
                # logger.log(datazzz)

                # request_url = urllib.request.urlopen(rs_playlist_url)
                # parse_url = urlparse(rs_playlist_url)

                # with urllib.request.urlopen(rs_playlist_url) as url:
                #     rspl_json_text = url.read().decode()
                # logger.log(rspl_json_text)
                # self.raw_playlist = data[0]

                # from_dict = RSPLTreeNode.from_dict(json.loads(rspl_json_text))
                #
                # data = json.loads(rspl_json_text)
                #
                # loads = json.loads(data['playlist'])[1]
                # logger.log("type(data)" + str(type(data)))
                #
                # rs_playlist = data['playlist']
                # logger.log("type(rs_playlist)" + str(type(rs_playlist)))
                # playlist_0 = rs_playlist[0]
                # dlc_set_ = playlist_0['dlc_set']
                # logger.warning("type(dlc_set_)" + str(type(dlc_set_)))
                # logger.warning(dlc_set_)
                # logger.warning(dlc_set_[0])
                # logger.warning(dlc_set_[1])
                # logger.warning(data)

                # for song in data['playlist']:
                #     logger.log(song['position'])
                #     artist_title = song['string']
                #     logger.log(artist_title)
                #     artist_title_split = artist_title.split("-")
                #     logger.log(artist_title_split)
                #     if len(artist_title_split) > 1:
                #         artist = artist_title_split[0].strip()
                #         title = artist_title_split[1].strip()
                #         logger.log(artist)
                #         logger.log(title)
                #         with con:
                #             cur = con.cursor()
                #             execute = cur.execute("SELECT colFileName FROM songs where colArtist like ? and colTitle like ?",
                #                                   ("%" + artist + "%", "%" + title + "%"))

                # rows = execute.fetchall()
                #
                # for element in rows:
                #     logger.debug("rows" + str(element))
                #
                # con.commit()
                #
                # logger.log(song['dlc_set'])
