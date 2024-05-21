import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Servant script for managing Rocksmith sessions.')
    parser.add_argument('-c', '--config', type=str, required=False, help='Configuration file path',
                        default='config/config.ini')
    args = parser.parse_args()
    config = args.config

    return config
