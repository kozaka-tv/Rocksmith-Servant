import json
import os

from munch import DefaultMunch

from utils import logger, file_utils

MODULE_NAME = "CDLCImporter"

NL = os.linesep

columns = ['rowId', 'colArtist', 'colTitle', 'colAlbum', 'colKey', 'colArrangements', 'colTunings', 'colSongLength',
           'colRepairStatus', 'colSongYear', 'colSongVolume', 'colFileName', 'colFileDate', 'colAppID',
           'colPackageAuthor', 'colPackageVersion', 'colTagged', 'colIgnitionID', 'colIgnitionDate',
           'colIgnitionVersion', 'colIgnitionAuthor', 'colArtistTitleAlbum', 'colArtistTitleAlbumDate', 'colArtistSort']


class CDLCImporter:
    def __init__(self, config_data, db):
        self.enabled = config_data.cdlc_importer.enabled
        if self.enabled:
            self.cdlc_import_json_file = config_data.cdlc_importer.cdlc_import_json_file
        # TODO should be behind the enabled check?
        self.db = db

    def load(self):
        if self.enabled:
            logger.log("-----------------------------------", MODULE_NAME)
            logger.warning("Importing CDLC files from CFSM json file...", MODULE_NAME)

            try:
                self.init_db()
            except Exception as e:
                logger.error("Database init error: {0}".format(e))
                raise e

            try:
                self.import_cdlc_files()
            except Exception as e:
                logger.error("Could not import CDLCs to the Database: {0}".format(e))
                raise e

            logger.log("-----------------------------------", MODULE_NAME)

    def create_tables(self):
        cursor = self.db.cursor()
        read = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "create_table_songs.sql")).read()
        cursor.executescript(read)

    def init_db(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='songs'")
        if cursor.fetchone()[0] == 1:
            logger.debug("Songs Table already exists, do not need to create it.", MODULE_NAME)
        else:
            logger.warning("Songs Table does not exists! Creating...", MODULE_NAME)
            self.create_tables()
        self.db.commit()

    # def file_datetime(filename):
    #     file_time = os.path.getmtime(filename)
    #     formatted_time = datetime.fromtimestamp(file_time)
    #     print("File datetime: {0}".format(formatted_time))
    #     return formatted_time

    # TODO the datetime check is not necessary probably, if we merge the data into the database and
    #  do not create a new one at every start. This means, that if the song is already in the Database,
    #  then we do not insert.
    # file_datetime(CDLC_IMPORT_JSON_FILE)

    @staticmethod
    def load_cfsm_song_data(json_file):
        json_file_read = json_file.read()
        json_file_data = json.loads(json_file_read)
        songs = dict(json_file_data)
        json_data = songs['dgvSongsMaster']
        return DefaultMunch.fromDict(json_data)

    def get_song_from_db_via_file_name(self, file_name):
        cur = self.db.cursor()
        # TODO maybe add internal ID for each song and get that ID here?
        execute = cur.execute("SELECT distinct colFileName FROM songs where colFileName like (?)", (file_name,))
        rows = execute.fetchall()
        return rows

    def insert_songs_to_db(self, songs):
        logger.debug("Start insert {} songs ...".format(len(songs)), MODULE_NAME)

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

        c = self.db.cursor()
        c.executemany(insert_query, values)
        values.clear()
        self.db.commit()
        c.close()

        logger.debug("... {} songs inserted.".format(len(songs)), MODULE_NAME)

    def import_cdlc_files(self):
        with open(self.cdlc_import_json_file, encoding='utf-8-sig') as json_file:
            logger.log("File to import: {}".format(json_file.name), MODULE_NAME)

            # TODO what exactly identifies a song in the DB? colFileName? colKey? colArtistTitleAlbumDate? All?
            count_songs_to_import = 0
            songs_to_import = []
            for cfsm_song_data in self.load_cfsm_song_data(json_file):
                count_songs_to_import += 1

                with self.db:
                    songs_from_db = self.get_song_from_db_via_file_name(
                        file_utils.replace_dlc_and_cdlc(cfsm_song_data.colFileName))

                    if len(songs_from_db) == 0:
                        logger.debug("New CDLC found: {}".format(cfsm_song_data.colFileName), MODULE_NAME)
                        songs_to_import.append(cfsm_song_data)

            if len(songs_to_import) == 0:
                logger.log(
                    "All {} songs from the import file is already exists in the Database, so nothing must be imported! "
                    "File: {}".format(count_songs_to_import, json_file.name), MODULE_NAME)
            else:
                logger.log("Will import {} new CDLC files into the DB.".format(len(songs_to_import)), MODULE_NAME)
                self.insert_songs_to_db(songs_to_import)
                logger.log(
                    "From {} songs, {} new CDLC were imported into the DB.".format(count_songs_to_import,
                                                                                   len(songs_to_import)), MODULE_NAME)
