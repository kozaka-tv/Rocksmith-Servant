import os
from unittest.mock import patch, PropertyMock

import pytest

from config.config_reader import ConfigReader


# Fixtures
@pytest.fixture
def mock_file_utils():
    with patch('utils.file_utils.create_directory_logged') as mock_create_directory_logged:
        yield mock_create_directory_logged


@pytest.fixture
def mock_logging():
    with patch('config.config_reader.log') as mock_log:
        yield mock_log


@pytest.fixture
def config_file_path(tmp_path):
    config_file = tmp_path / "config.ini"
    config_file.write_text(
        "[RockSniffer]\nhost = localhost\nport = 1234\nenabled = True\n[SongLoader]\ncdlc_archive_dir = /some/dir\nrocksmith_cdlc_dir = /another/dir\nallow_load_when_in_game = False\n")
    return str(config_file)


@pytest.fixture
def mock_serialized():
    mock_data = {
        "RockSniffer": {
            "enabled": False,
            "host": "localhost",
            "port": "1234",
        },
        "SetlistLogger": {
            "enabled": False,
            "setlist_path": "<Enter your directory where do you want to have your Setlist>",
        },
        "SongLoader": {
            "enabled": False,
            "twitch_channel": "<Enter your Twitch channel name>",
            "phpsessid": "<Enter your PHP Session ID from the cookie of the RS Playlist after login. "
                         "You may enter more than one ID, separated by ';'>",
            "rspl_tag_to_download": "<Create a tag in RS Playlist for song need to be downloaded and enter to here>",
            "rspl_tag_downloaded": "<Create a tag in RS Playlist for song which has been downloaded and enter to here>",
            "rspl_tag_loaded": "<Create a tag in RS Playlist for song loaded under RS and enter to here>",
            "rspl_tag_new_viewer_request": "<Create a tag in RS Playlist for song which one has been requested by a "
                                           "new viewer and enter to here>",
            "rspl_tag_raider_request": "<Create a tag in RS Playlist for song which one has been requested by a "
                                       "raider streamer and enter to here>",
            "rspl_tag_vip_viewer_request": "<Create a tag in RS Playlist for song which one has been requested by a "
                                           "channel VIP viewer and enter to here>",
            "cdlc_archive_dir": "<Enter your CDLC archive directory, where you store all of your downloaded CDLCs>",
            "rocksmith_cdlc_dir": "<Enter your Rocksmith CDLC directory, where you have all the loaded CDLC songs>",
            "allow_load_when_in_game": True,
            "cdlc_import_json_file": "<Enter your directory, where do you want put your json file from CFSM, "
                                     "what contains all your CDLC files need to be imported into the Servant database>"
        },
        "SceneSwitcher": {
            "enabled": False,
        },
        "FileManager": {
            "enabled": False,
            "download_dirs": "<Enter source directories (separated by ';') from where do you want to move CDLC files>",
            "destination_dir": "<Enter your directory to where do you want to move CDLC files>",
            "using_cfsm": False,
        }
    }
    with patch.dict('config.config_ini_template.serialized', mock_data, clear=True) as mock:
        print("Mock Serialized Applied:", mock_data)
        yield mock


@pytest.fixture
def config_reader(config_file_path, mock_serialized):
    return ConfigReader(config_file_path)


def test_initialization(mock_file_utils, mock_logging, config_file_path):
    expected_dirname = os.path.dirname(config_file_path)
    expected_basename = os.path.basename(config_file_path)
    expected_abspath = os.path.abspath(config_file_path)

    actual = ConfigReader(config_file_path)

    assert actual.config_file_path == config_file_path
    assert actual.config_dirname == expected_dirname
    assert actual.config_filename == expected_basename
    assert actual.config_abspath == expected_abspath

    mock_file_utils.assert_called_once_with(expected_dirname)
    mock_logging.warning.assert_any_call('Loading config from %s ...', expected_abspath)

    assert actual.last_modified is not None


def test_load_content_from_config(mock_serialized, config_reader):
    # Debugging: Print the current content of the configuration to verify the values
    print("Config Content:", dict(config_reader.content.items('RockSniffer')))

    assert config_reader.content.get('RockSniffer', 'host') == 'localhost'
    assert config_reader.content.get('RockSniffer', 'port') == '1234'
    assert config_reader.content.get('RockSniffer', 'enabled') == 'True'


def test_if_needed_create_config_from_template_and_then_stop(mock_logging, config_file_path):
    empty_config_file_path = config_file_path + "_empty"
    with open(empty_config_file_path, 'w', encoding='utf-8') as f:
        f.write("")

    config_reader = ConfigReader(empty_config_file_path)

    with patch('config.config_reader.ConfigReader._ConfigReader__last_modification_time',
               new_callable=PropertyMock) as mock_last_modification_time:
        mock_last_modification_time.return_value = 0
        with patch('sys.exit') as mock_exit, patch('builtins.input', return_value=''):
            print(f"Running __if_needed_create_config_from_template_and_then_stop for {empty_config_file_path}")
            config_reader._ConfigReader__if_needed_create_config_from_template_and_then_stop()
            print(f"Checking if sys.exit was called...")
            mock_exit.assert_called_once()
            print(f"Checking if log.error was called...")
            mock_logging.error.assert_called_once_with(
                'Because this is the first run, and no configuration file was found, '
                'I just created the %s configuration file for you!', config_reader.config_abspath)


# Configuration Values Tests
def test_get_int_value(config_reader):
    assert config_reader.get_int_value('RockSniffer', 'port') == 1234


def test_get_bool_value(config_reader):
    assert config_reader.get_bool('RockSniffer', 'enabled')


def test_get_list_value(mock_serialized, config_file_path):
    with open(config_file_path, 'w', encoding='utf-8') as f:
        f.write("[TestSection]\nkey = value1; value2; value3")
    reader = ConfigReader(config_file_path)
    assert reader.get_list('TestSection', 'key') == ['value1', 'value2', 'value3']


def test_get_set_value(mock_serialized, config_file_path):
    with open(config_file_path, 'w', encoding='utf-8') as f:
        f.write("[TestSection]\nkey = value1; value2; value3")
    reader = ConfigReader(config_file_path)
    assert reader.get_set('TestSection', 'key') == {'value1', 'value2', 'value3'}


# Logging Configuration Tests
def test_log_config(mock_logging, config_reader):
    config_reader._ConfigReader__log_config()
    mock_logging.warning.assert_any_call('------- CONFIG ------------------------------------------------')
    mock_logging.info.assert_any_call('RockSniffer.host = %s', 'localhost')
    mock_logging.info.assert_any_call('RockSniffer.port = %s', '1234')
    mock_logging.info.assert_any_call('SongLoader.cdlc_archive_dir = %s', '/some/dir')
    mock_logging.info.assert_any_call('SongLoader.rocksmith_cdlc_dir = %s', '/another/dir')
    mock_logging.info.assert_any_call('SongLoader.allow_load_when_in_game = %s', 'False')


# Handling Bad Values Tests
def test_replace_bad_value(mock_serialized, config_reader):
    # Print the serialized dictionary for debugging
    print("Serialized Dictionary in Test (mock_serialized):", mock_serialized)

    # Print the serialized dictionary used by ConfigReader for debugging
    from config.config_ini_template import serialized as actual_serialized
    print("Serialized Dictionary in Test (actual_serialized):", actual_serialized)

    # Set a bad value to trigger replacement
    config_reader.content.set('RockSniffer', 'port', 'bad_value')

    # Print the configuration after setting the bad value
    print("Config Port Value after setting bad value:", config_reader.content.get('RockSniffer', 'port'))

    # Manually invoke the method to replace bad value with default value
    config_reader._ConfigReader__replace_bad_value('RockSniffer', 'port', int)

    # Debugging: Print the config value after replacement
    print("Serialized Port Value (mock_serialized):", mock_serialized['RockSniffer']['port'])
    print("Serialized Port Value (actual_serialized):", actual_serialized['RockSniffer']['port'])
    print("Config Port Value after replacement:", config_reader.content.get('RockSniffer', 'port'))

    assert config_reader.content.get('RockSniffer', 'port') == '1234'


def test_retain_good_value(mock_serialized, config_reader):
    # Ensure the initial good value is correct
    initial_value = config_reader.content.get('RockSniffer', 'port')
    print("Initial Config Port Value:", initial_value)

    # Manually invoke the method to replace bad value with default value
    config_reader._ConfigReader__replace_bad_value('RockSniffer', 'port', int)

    # Debugging: Print the config value after replacement
    print("Config Port Value after retaining good value:", config_reader.content.get('RockSniffer', 'port'))

    # Ensure the good value remains unchanged
    assert config_reader.content.get('RockSniffer', 'port') == initial_value


# def test_log_bad_value_message(mock_logging, config_reader):
#    # Directly setting a bad value in the config to trigger the error
#    config_reader.content.set('RockSniffer', 'enabled', 'not_a_bool')
#    try:
#        # Trigger the method that causes the log message by trying to get a boolean value
#        config_reader.get('RockSniffer', 'enabled', bool)
#    except ValueError:
#        # Explicitly invoke the __log_bad_value_message method for the test
#        config_reader._ConfigReader__log_bad_value_message('RockSniffer', 'enabled', bool)
#
#    # Print actual log call arguments for debugging
#    for call in mock_logging.method_calls:
#        print("Log call:", call)
#
#    # Check the error log message
#    mock_logging.error.assert_called_with(
#        'Error retrieving value from %s for section [%s] with key [%s].',
#        config_reader.config_abspath, 'RockSniffer', 'enabled'
#    )
#
#    # Check the warning log message
#    mock_logging.warning.assert_any_call(
#        "For this type of key, please use either False, No, 0 or True, Yes, 1"
#    )


def test_log_bad_value_message_direct(mock_logging, config_reader):
    # Directly invoke the __log_bad_value_message method to ensure it logs the correct messages
    config_reader._ConfigReader__log_bad_value_message('RockSniffer', 'port', bool)

    # Check the error log message
    mock_logging.error.assert_called_with(
        'Error retrieving value from %s for section [%s] with key [%s].',
        config_reader.config_abspath, 'RockSniffer', 'port'
    )

    # Print actual warning call arguments for debugging
    for call in mock_logging.warning.call_args_list:
        print("Actual warning call:", call)

    # Check the warning log message
    mock_logging.warning.assert_any_call(
        "For this type of key, please use either False, No, 0 or True, Yes, 1"
    )


# Saving Configuration Test
def test_save_config(config_reader):
    # Modify the config to trigger a save
    config_reader.content.set('RockSniffer', 'host', 'new_host')

    # Save the config
    config_reader._ConfigReader__save()

    # Reload the config and check the saved value
    new_reader = ConfigReader(config_reader.config_file_path)
    assert new_reader.content.get('RockSniffer', 'host') == 'new_host'


# Error Handling in the `get` Method Test
def test_get_method_error_handling(mock_logging, config_reader):
    # Set a bad value to trigger error handling
    config_reader.content.set('RockSniffer', 'port', 'bad_value')

    # Capture the log output
    with patch('config.config_reader.log') as mock_log:
        config_reader.get('RockSniffer', 'port', int)

        # Verify that the error was logged
        mock_log.error.assert_called_with(
            'Error retrieving value from %s for section [%s] with key [%s].',
            config_reader.config_abspath, 'RockSniffer', 'port'
        )


# Ensuring Configuration Directory Creation Test
def test_create_directory(mock_file_utils, config_file_path):
    ConfigReader(config_file_path)
    mock_file_utils.assert_called_once_with(os.path.dirname(config_file_path))


# Correct Configuration File Path Test
def test_config_file_path(config_file_path):
    reader = ConfigReader(config_file_path)
    assert reader.config_abspath == os.path.abspath(config_file_path)
