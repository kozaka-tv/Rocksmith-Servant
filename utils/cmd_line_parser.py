import argparse
import os

from definitions import ROOT_DIR


def parse_args():
    parser = argparse.ArgumentParser(description='Servant script for managing Rocksmith sessions.')
    parser.add_argument('-c', '--config', default='config' + os.sep + 'config.ini',
                        help='Path of the configuration file like: config' + os.sep + 'my_config.ini')
    parser.add_argument('-db', '--database', default='servant.db',
                        help='Path of the database file like: my_database.db')

    args = parser.parse_args()

    config = os.path.join(ROOT_DIR, args.config)
    if not config.endswith('.ini'):
        raise ValueError("The configuration file must have a '.ini' extension.")

    database = os.path.join(ROOT_DIR, args.database)
    if not database.endswith('.db'):
        raise ValueError("The database file must have a '.db' extension.")

    return config, database
