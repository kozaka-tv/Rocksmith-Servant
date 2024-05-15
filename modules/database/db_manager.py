import logging
import os
import sqlite3

from modules.song_loader.song_data import SongData
from utils import string_utils
from utils.collection_utils import set_of_the_tuples_from_the_first_position
from utils.string_utils import remove_special_chars

DATABASE = './servant.db'
log = logging.getLogger()


class DBManager:

    def __init__(self):
        self.dirname = self.__get_db_dirname()

        self.db = sqlite3.connect(DATABASE)
        self.__init_db()

    def __init_db(self):
        try:
            self.__create_table("create_table_songs.sql")
            self.__create_table("create_table_songs_enhanced.sql")
        except Exception as e:
            log.error("%s Database init error: %s", type(e), e)
            raise e

    def __create_table(self, sql_file_name):
        cursor = self.db.cursor()
        sql_file = os.path.join(self.dirname, sql_file_name)
        read_sql_file = open(sql_file, encoding="utf-8").read()
        cursor.executescript(read_sql_file)
        self.db.commit()

    @staticmethod
    def __get_db_dirname():
        return os.path.dirname(os.path.abspath(__file__))

    def __get_songs_from_db(self, artist, title):
        cur = self.db.cursor()
        # TODO add and colTagged != 'ODLC'?
        songs = cur.execute("SELECT distinct colFileName FROM songs where colArtist like ? and colTitle like ?",
                            ("%" + artist + "%", "%" + title + "%")).fetchall()
        return set_of_the_tuples_from_the_first_position(songs)

    def search_song_by_artist_and_title(self, artist, title):
        # TODO make a special search for similar words in artist and title
        songs_from_db_without_special_chars = self.__get_songs_from_db(remove_special_chars(artist),
                                                                       remove_special_chars(title))
        return self.__get_songs_from_db(artist, title).union(songs_from_db_without_special_chars)

    def search_song_by_filename(self, filename: str):
        cur = self.db.cursor()
        song = cur.execute("SELECT colFileName, colArtist, colTitle FROM songs where songs.colFileName = ?",
                           ("" + filename,)).fetchone()

        if song is None:
            return None

        song_data = SongData()
        song_data.song_file_name = song[0]
        song_data.artist = song[1]
        song_data.title = song[2]

        return song_data

    def is_song_by_filename_exists(self, filename):
        cur = self.db.cursor()
        execute = cur.execute("select count(*) from songs where colFilename = ?", ("" + filename,))
        fetchone = execute.fetchone()[0]
        return fetchone != 0

    def insert_song(self, song_data):
        cur = self.db.cursor()
        sql = (("insert into songs ("
                "colArtist, "
                "colTitle, "
                "colFileName) " +
                "values ('")
               + string_utils.escape_single_quote(song_data.artist) + "', '"
               + string_utils.escape_single_quote(song_data.title) + "', '"
               + string_utils.escape_single_quote(song_data.song_file_name) + "')")
        cur.execute(sql)
        self.db.commit()

    def all_song_filenames(self):
        cur = self.db.cursor()
        all_elements_tuple = cur.execute("SELECT distinct colFileName FROM songs").fetchall()
        return set_of_the_tuples_from_the_first_position(all_elements_tuple)

    def delete_song_by_filename(self, to_delete):
        cur = self.db.cursor()
        sql = f"delete FROM songs WHERE songs.colFileName in ({','.join(['?'] * len(to_delete))})"
        cur.execute(sql, tuple(to_delete))
        self.db.commit()
