import sqlite3

from utils import string_utils

con = sqlite3.connect('./servant.db')


def get_songs_from_db(artist, title):
    cur = con.cursor()
    # TODO add and colTagged != 'ODLC'?
    execute = cur.execute("SELECT distinct colFileName FROM songs where colArtist like ? and colTitle like ?",
                          ("%" + artist + "%", "%" + title + "%"))
    return execute.fetchall()


def search_song_in_the_db(artist, title):
    rows = get_songs_from_db(artist, title)
    # TODO hm...maybe remove special chars and do a second query. To load all possible variations?
    # TODO make a special search for similar words in artist and title
    # So not only if len(rows) <= 0
    if len(rows) <= 0:
        # remove special chars
        artist_norm = string_utils.remove_special_chars(artist)
        title_norm = string_utils.remove_special_chars(title)
        rows = get_songs_from_db(artist_norm, title_norm)
    return rows
