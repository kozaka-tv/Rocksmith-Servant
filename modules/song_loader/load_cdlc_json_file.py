import json
import os
import sqlite3
from datetime import datetime

from munch import DefaultMunch

from modules.song_loader import song_loader_helper
from utils import logger

CDLC_IMPORT_JSON_FILE = 'c:/Google Drive Kozaka/Kozaka - Live Stream/SongsMasterGrid.json'
# CDLC_IMPORT_JSON_FILE = '../../import/SongsMasterGrid.json'
# CDLC_IMPORT_JSON_FILE = '../../import/SongsMasterGrid_BIG.json'
# CDLC_IMPORT_JSON_FILE = '../../import/SongsMasterGrid_SMALL.json'

db = sqlite3.connect('../../servant.db')

columns = ['rowId', 'colArtist', 'colTitle', 'colAlbum', 'colKey', 'colArrangements', 'colTunings', 'colSongLength',
           'colRepairStatus', 'colSongYear', 'colSongVolume', 'colFileName', 'colFileDate', 'colAppID',
           'colPackageAuthor', 'colPackageVersion', 'colTagged', 'colIgnitionID', 'colIgnitionDate',
           'colIgnitionVersion', 'colIgnitionAuthor', 'colArtistTitleAlbum', 'colArtistTitleAlbumDate', 'colArtistSort']


def create_tables():
    cursor = db.cursor()
    read = open("create_table_songs.sql").read()
    cursor.executescript(read)


def init_db():
    cursor = db.cursor()
    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='songs'")
    if cursor.fetchone()[0] == 1:
        logger.debug("Songs Table exists.")
    else:
        logger.warning("Songs Table does not exists! Creating...")
        create_tables()
    db.commit()


def file_datetime(filename):
    file_time = os.path.getmtime(filename)
    formatted_time = datetime.fromtimestamp(file_time)
    print("File datetime: {0}".format(formatted_time))
    return formatted_time


# TODO the datetime check is not necessary probably, if we merge the data into the database and
#  do not create a new one at every start. This means, that if the song is already in the Database,
#  then we do not insert.
file_datetime(CDLC_IMPORT_JSON_FILE)


def load_cfsm_song_data(json_file):
    json_file_read = json_file.read()
    json_file_data = json.loads(json_file_read)
    songs = dict(json_file_data)
    json_data = songs['dgvSongsMaster']
    return DefaultMunch.fromDict(json_data)


def get_song_from_db_via_file_name(file_name):
    cur = db.cursor()
    # TODO maybe add internal ID for each song and get that ID here?
    execute = cur.execute("SELECT distinct colFileName FROM songs where colFileName like (?)", (file_name,))
    rows = execute.fetchall()
    return rows


def insert_songs_to_db(songs):
    logger.debug("Start insert {} songs ...".format(len(songs)))

    value = []
    values = []
    for song in songs:
        for column in columns:
            if column == 'colFileName':
                value.append(
                    str(song.get(column)).strip().replace('cdlc\\', '').replace('dlc\\', ''))
            else:
                value.append(str(song.get(column)).strip())
        values.append(list(value))
        value.clear()

    insert_query = "insert into songs ({0}) values (?{1})".format(",".join(columns), ",?" * (len(columns) - 1))

    c = db.cursor()
    c.executemany(insert_query, values)
    values.clear()
    db.commit()
    c.close()

    logger.debug("... {} songs inserted.".format(len(songs)))


def import_cdlc_files():
    with open(CDLC_IMPORT_JSON_FILE, encoding='utf-8-sig') as json_file:
        logger.log("File to import: {}".format(json_file.name))

        # TODO what exactly identifies a song in the DB? colFileName? colKey? colArtistTitleAlbumDate? All?
        count_songs_to_import = 0
        songs_to_import = []
        for cfsm_song_data in load_cfsm_song_data(json_file):
            count_songs_to_import += 1

            with db:
                songs_from_db = get_song_from_db_via_file_name(
                    song_loader_helper.replace_dlc_and_cdlc(cfsm_song_data.colFileName))

                if len(songs_from_db) == 0:
                    logger.debug("New CDLC found: {}".format(cfsm_song_data.colFileName))
                    songs_to_import.append(cfsm_song_data)

        if len(songs_to_import) == 0:
            logger.log(
                "All {} songs from the import file is already exists in the Database, so nothing must be imported! "
                "File: {}".format(count_songs_to_import, json_file.name))
        else:
            logger.log("Will import {} new CDLC files into the DB.".format(len(songs_to_import)))
            insert_songs_to_db(songs_to_import)
            logger.log(
                "From {} songs, {} new CDLC were imported into the DB.".format(count_songs_to_import,
                                                                               len(songs_to_import)))


init_db()
import_cdlc_files()
