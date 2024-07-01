import logging
import os
import sqlite3
from typing import Optional

from modules.song_loader.song_data import SongData, ArtistTitle
from utils.collection_utils import get_tuples_from_the_first_position_of
from utils.string_utils import normalize, escape_single_quote

log = logging.getLogger()


class DBManager:

    def __init__(self, db_file):
        log.info('Database path: %s', db_file)

        self.dirname = self.__get_db_dirname()

        self.db = sqlite3.connect(db_file)
        self.__init_db()

    def __init_db(self):
        try:
            self.__create_table("create_table_songs.sql")
        except Exception as e:
            log.error("%s Database init error: %s", type(e), e)
            raise e

    def __create_table(self, sql_file_name):
        cursor = self.db.cursor()
        sql_file = os.path.join(self.dirname, sql_file_name)
        with open(sql_file, encoding="utf-8") as file:
            read_sql_file = file.read()
        cursor.executescript(read_sql_file)
        self.db.commit()

    @staticmethod
    def __get_db_dirname():
        return os.path.dirname(os.path.abspath(__file__))

    def __get_songs_from_db(self, artist, title):
        cur = self.db.cursor()
        songs = cur.execute("SELECT distinct fileName FROM songs where artist like ? and title like ?",
                            ("%" + artist + "%", "%" + title + "%")).fetchall()
        return get_tuples_from_the_first_position_of(songs)

    def search_song_by_artist_and_title(self, artist, title):
        songs_from_db_without_special_chars = self.__get_songs_from_db(normalize(artist),
                                                                       normalize(title))
        return self.__get_songs_from_db(artist, title).union(songs_from_db_without_special_chars)

    def search_song_by_filename(self, filename: str) -> Optional[SongData]:
        cur = self.db.cursor()
        song = cur.execute("SELECT fileName, artist, title FROM songs where songs.fileName = ?",
                           ("" + filename,)).fetchone()

        if song is None:
            return None

        return SongData(song_filename=(song[0]), artist_title=ArtistTitle(song[1], song[2]))

    def is_song_by_filename_exists(self, filename):
        cur = self.db.cursor()
        execute = cur.execute("select count(*) from songs where filename = ?", ("" + filename,))
        fetchone = execute.fetchone()[0]
        return fetchone != 0

    def insert_song(self, song_data: SongData):
        cur = self.db.cursor()
        sql = (
                ("insert into songs ("
                 "artist, "
                 "title, "
                 "artistNormalized, "
                 "titleNormalized, "
                 "fileName"
                 ") " +
                 "values ('")
                + escape_single_quote(song_data.artist_title.artist) + "', '"
                + escape_single_quote(song_data.artist_title.title) + "', '"
                + escape_single_quote(song_data.artist_title.artist_normalized()) + "', '"
                + escape_single_quote(song_data.artist_title.title_normalized()) + "', '"
                + escape_single_quote(song_data.song_filename)
                + "')"
        )
        cur.execute(sql)
        self.db.commit()

    def all_song_filenames(self):
        cur = self.db.cursor()
        all_songs = cur.execute("SELECT distinct fileName FROM songs").fetchall()
        return get_tuples_from_the_first_position_of(all_songs)

    def delete_song_by_filename(self, to_delete):
        cur = self.db.cursor()
        sql = f"delete FROM songs WHERE songs.fileName in ({','.join(['?'] * len(to_delete))})"
        cur.execute(sql, tuple(to_delete))
        self.db.commit()
