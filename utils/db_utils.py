import sqlite3

con = sqlite3.connect('./servant.db')


def get_songs_from_db(artist, title):
    cur = con.cursor()
    # TODO add and colTagged != 'ODLC'?
    execute = cur.execute("SELECT distinct colFileName FROM songs where colArtist like ? and colTitle like ?",
                          ("%" + artist + "%", "%" + title + "%"))
    return execute.fetchall()
