from unittest.mock import patch

import pytest

from utils.cmd_line_parser import parse_args


@patch('sys.argv', ['run.py'])
def test_defaults():
    config, database = parse_args()
    assert config == 'config.ini'
    assert database == 'servant.db'


@patch('sys.argv', ['run.py', '-c', 'custom_config.ini'])
def test_custom_config_with_c():
    config, database = parse_args()
    assert config == 'custom_config.ini'
    assert database == 'servant.db'


@patch('sys.argv', ['run.py', '--config', 'custom_config.ini'])
def test_custom_config_with_config():
    config, database = parse_args()
    assert config == 'custom_config.ini'
    assert database == 'servant.db'


@patch('sys.argv', ['run.py', '-db', 'custom_servant.db'])
def test_custom_database_with_db():
    config, database = parse_args()
    assert config == 'config/config.ini'
    assert database == 'custom_servant.db'


@patch('sys.argv', ['run.py', '--database', 'custom_servant.db'])
def test_custom_database_with_database():
    config, database = parse_args()
    assert config == 'config/config.ini'
    assert database == 'custom_servant.db'


@patch('sys.argv', ['run.py', '-c', 'custom_config.ini', '-db', 'custom_servant.db'])
def test_custom_config_and_database():
    config, database = parse_args()
    assert config == 'custom_config.ini'
    assert database == 'custom_servant.db'


@patch('sys.argv', ['run.py', '-c', 'custom_config.txt'])
def test_invalid_config_extension():
    with pytest.raises(ValueError, match="The configuration file must have a '.ini' extension."):
        parse_args()


@patch('sys.argv', ['run.py', '-db', 'custom_servant.txt'])
def test_invalid_database_extension():
    with pytest.raises(ValueError, match="The database file must have a '.db' extension."):
        parse_args()
