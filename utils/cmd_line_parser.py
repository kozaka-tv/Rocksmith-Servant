import argparse

DEFAULT_CONFIG_INI = 'config.ini'
DEFAULT_SERVANT_DB = 'servant.db'


def parse_args():
    parser = argparse.ArgumentParser(description='Servant script for managing Rocksmith sessions.')
    parser.add_argument('-c', '--config', default=DEFAULT_CONFIG_INI,
                        help='Path of the configuration file like: my_config.ini')
    parser.add_argument('-db', '--database', default=DEFAULT_SERVANT_DB,
                        help='Path of the database file like: my_database.db')

    args = parser.parse_args()

    config = args.config
    if not config.endswith('.ini'):
        raise ValueError("The configuration file must end with an '.ini' extension! config: " + config)

    database = args.database
    if not database.endswith('.db'):
        raise ValueError("The database file must end with an '.db' extension! database: " + database)

    return config, database
