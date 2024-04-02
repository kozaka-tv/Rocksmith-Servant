import logging
import os
import sqlite3

from utils import string_utils

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
        execute = cur.execute("SELECT distinct colFileName FROM songs where colArtist like ? and colTitle like ?",
                              ("%" + artist + "%", "%" + title + "%"))
        return execute.fetchall()

    def search_song_in_the_db(self, artist, title):
        rows = self.__get_songs_from_db(artist, title)
        # TODO hm...maybe remove special chars and do a second query. To load all possible variations?
        # TODO make a special search for similar words in artist and title
        # So not only if len(rows) <= 0
        if len(rows) <= 0:
            # remove special chars
            artist_norm = string_utils.remove_special_chars(artist)
            title_norm = string_utils.remove_special_chars(title)
            rows = self.__get_songs_from_db(artist_norm, title_norm)
        return rows

    def is_song_by_filename_exists(self, filename):
        cur = self.db.cursor()
        execute = cur.execute("select count(*) from songs where colFilename is ?", ("" + filename))
        fetchone = execute.fetchone()
        return fetchone != 0
