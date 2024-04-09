import json
import logging

from munch import DefaultMunch

from modules.database.db_manager import DBManager
from utils import file_utils

columns = ['colArtist', 'colTitle', 'colAlbum', 'colKey', 'colArrangements', 'colTunings', 'colSongLength',
           'colRepairStatus', 'colSongYear', 'colSongVolume', 'colFileName', 'colFileDate', 'colAppID',
           'colPackageAuthor', 'colPackageVersion', 'colTagged', 'colIgnitionID', 'colIgnitionDate',
           'colIgnitionVersion', 'colIgnitionAuthor', 'colArtistTitleAlbum', 'colArtistTitleAlbumDate', 'colArtistSort']

log = logging.getLogger()


class CDLCImporter:
    def __init__(self, config_data, db_manager: DBManager):
        self.enabled = config_data.cdlc_importer.enabled
        if self.enabled:
            self.cdlc_import_json_file = config_data.cdlc_importer.cdlc_import_json_file

        self.db = db_manager.db

    def load(self):
        if self.enabled:
            log.info("-----------------------------------")
            # TODO update this log, as in the future no CFSM import file is actually needed,
            #  if CDLC data is extracted from files
            log.warning("Importing CDLC files from CFSM json file...")

            # TODO commented out STREAM old solution to import CFSM file
            # TODO commented out STREAM old solution to import CFSM file
            # TODO commented out STREAM old solution to import CFSM file
            # TODO commented out STREAM old solution to import CFSM file
            # TODO commented out STREAM old solution to import CFSM file
            # self.import_cdlc_files()

            # TODO implement this
            self.extract_song_information()

            log.info("-----------------------------------")

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
        log.debug("Start insert %s songs ...", len(songs))

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

        cursor = self.db.cursor()
        cursor.executemany(insert_query, values)
        values.clear()
        self.db.commit()
        cursor.close()

        log.debug("... %s songs inserted.", len(songs))

    def import_cdlc_files(self):
        try:
            with open(self.cdlc_import_json_file, encoding='utf-8-sig') as json_file:
                log.info("File to import: %s", json_file.name)

                # TODO what exactly identifies a song in the DB? colFileName? colKey? colArtistTitleAlbumDate? All?
                count_songs_to_import = 0
                songs_to_import = []
                for cfsm_song_data in self.load_cfsm_song_data(json_file):
                    count_songs_to_import += 1

                    with self.db:
                        songs_from_db = self.get_song_from_db_via_file_name(
                            file_utils.replace_dlc_and_cdlc(cfsm_song_data.colFileName))

                        if len(songs_from_db) == 0:
                            log.info("New CDLC found: %s", cfsm_song_data.colFileName)
                            songs_to_import.append(cfsm_song_data)

                if len(songs_to_import) == 0:
                    log.info(
                        "All %s songs from the import file is already exists in the Database so "
                        "nothing must be imported! File: %s", count_songs_to_import, json_file.name)
                else:
                    log.info("Will import %s new CDLC files into the DB.", len(songs_to_import))
                    self.insert_songs_to_db(songs_to_import)
                    log.info("From %s songs, %s new CDLC were imported into the DB.",
                             count_songs_to_import, len(songs_to_import))

        except Exception as e:
            log.error("%s Could not import CDLCs to the Database: %s", type(e), e)
            raise e

    # TODO need to implement this
    def extract_song_information(self):
        try:
            log.error("TODO Dummy log: %s", self.enabled)

        except Exception as e:
            log.error("%s Could not import CDLCs to the Database: %s", type(e), e)
            raise e
