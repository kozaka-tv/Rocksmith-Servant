import logging
import os
import sqlite3

from utils import string_utils
from utils.collection_utils import set_of_the_tuples_from_the_first_position

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

    def search_song_in_the_db(self, artist, title):
        # TODO make a special search for similar words in artist and title
        return self.__get_songs_from_db(artist, title).union(
            self.__get_songs_from_db(string_utils.remove_special_chars(artist),
                                     string_utils.remove_special_chars(title)))

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
