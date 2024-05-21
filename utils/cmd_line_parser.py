import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Servant script for managing Rocksmith sessions.')
    parser.add_argument('-c', '--config', type=str, required=False, help='Configuration file path',
                        default='config/config.ini')
    parser.add_argument('-db', '--database', type=str, required=False, help=' file path',
                        default='servant.db')
    args = parser.parse_args()

    config = args.config
    database = args.database

    if not config.endswith('.ini'):
        raise ValueError("The configuration file must have a '.ini' extension.")
    if not database.endswith('.db'):
        raise ValueError("The database file must have a '.db' extension.")

    return config, database
