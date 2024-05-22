import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Servant script for managing Rocksmith sessions.')
    parser.add_argument('-c', '--config', default='config/config.ini',
                        help='Path of the configuration file like: config/my_config.ini')
    parser.add_argument('-db', '--database', default='servant.db',
                        help='Path of the database file like: my_database.db')

    args = parser.parse_args()

    config = args.config
    if not config.endswith('.ini'):
        raise ValueError("The configuration file must have a '.ini' extension.")

    database = args.database
    if not database.endswith('.db'):
        raise ValueError("The database file must have a '.db' extension.")

    return config, database
