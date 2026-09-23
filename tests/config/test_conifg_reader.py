import os
from unittest.mock import patch

import pytest

from config.config_reader import ConfigReader


# Fixtures
@pytest.fixture(name="mock_file_utils")
def fixture_mock_file_utils():
    with patch('utils.file_utils.create_directory_logged') as mock_create_directory_logged:
        yield mock_create_directory_logged

@pytest.fixture(name="mock_logging")
def fixture_mock_logging():
    with patch('config.config_reader.log') as mock_log:
        yield mock_log


@pytest.fixture(name="config_file_path")
def fixture_config_file_path(tmp_path):
    config_file = tmp_path / "config.ini"
    config_file.write_text(
        "[RockSniffer]\n"
        "host = localhost\n"
        "port = 1234\n"
        "enabled = True\n"
        "[SongLoader]\n"
        "cdlc_archive_dir = /some/dir\n"
        "rocksmith_cdlc_dir = /another/dir\n"
        "allow_load_when_in_game = False\n",
        encoding="utf-8",
    )
    return str(config_file)


@pytest.fixture(name="mock_serialized")
def fixture_mock_serialized():
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


@pytest.fixture(name="config_reader")
def fixture_config_reader(config_file_path, request):
    request.getfixturevalue("mock_serialized")
    request.getfixturevalue("mock_logging")

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


def test_load_content_from_config(config_reader):
    # Debugging: Print the current content of the configuration to verify the values
    print("Config Content:", dict(config_reader.content.items('RockSniffer')))

    assert config_reader.content.get('RockSniffer', 'host') == 'localhost'
    assert config_reader.content.get('RockSniffer', 'port') == '1234'
    assert config_reader.content.get('RockSniffer', 'enabled') == 'True'


def test_if_needed_create_config_from_template_and_then_stop(
    mock_logging, tmp_path
):
    config_file_path = tmp_path / "config.ini"

    # Simulate the first run without an existing configuration file.
    with patch("builtins.input", return_value=""):
        with pytest.raises(SystemExit):
            ConfigReader(str(config_file_path))

    # Verify that the configuration template was created.
    assert config_file_path.is_file()
    assert config_file_path.stat().st_size > 0

    # Verify that the user was informed about the new configuration file.
    mock_logging.error.assert_called_once_with(
        "Because this is the first run, and no configuration file was found, "
        "I just created the %s configuration file for you!",
        str(config_file_path),
    )


# Configuration Values Tests
def test_get_int_value(config_reader):
    assert config_reader.get_int_value('RockSniffer', 'port') == 1234


def test_get_bool_value(config_reader):
    assert config_reader.get_bool('RockSniffer', 'enabled')


def test_get_list_value(config_file_path):
    with open(config_file_path, 'w', encoding='utf-8') as f:
        f.write("[TestSection]\nkey = value1; value2; value3")

    reader = ConfigReader(config_file_path)

    assert reader.get_list('TestSection', 'key') == [
        'value1', 'value2', 'value3'
    ]


def test_get_set_value(config_file_path):
    with open(config_file_path, 'w', encoding='utf-8') as f:
        f.write("[TestSection]\nkey = value1; value2; value3")

    reader = ConfigReader(config_file_path)

    assert reader.get_set('TestSection', 'key') == {
        'value1', 'value2', 'value3'
    }


# Logging Configuration Tests
@pytest.mark.usefixtures("config_reader")
def test_log_config(mock_logging):
    # ConfigReader logs its configuration during initialization.
    mock_logging.warning.assert_any_call(
        '------- CONFIG ------------------------------------------------'
    )
    mock_logging.info.assert_any_call(
        'RockSniffer.host = %s', 'localhost'
    )
    mock_logging.info.assert_any_call(
        'RockSniffer.port = %s', '1234'
    )
    mock_logging.info.assert_any_call(
        'SongLoader.cdlc_archive_dir = %s', '/some/dir'
    )
    mock_logging.info.assert_any_call(
        'SongLoader.rocksmith_cdlc_dir = %s', '/another/dir'
    )
    mock_logging.info.assert_any_call(
        'SongLoader.allow_load_when_in_game = %s', 'False'
    )


# Handling Bad Values Tests
def test_replace_bad_value(config_reader):
    # Set a bad value to trigger replacement
    config_reader.content.set('RockSniffer', 'port', 'bad_value')

    # Retrieve the value and trigger automatic replacement
    result = config_reader.get('RockSniffer', 'port', int)

    # Verify that the invalid value was replaced with the default
    assert result == 1234
    assert config_reader.content.get('RockSniffer', 'port') == '1234'


def test_retain_good_value(config_reader):
    # Ensure the initial good value is correct
    initial_value = config_reader.content.get('RockSniffer', 'port')

    # Retrieve a valid value without triggering replacement
    result = config_reader.get('RockSniffer', 'port', int)

    # Ensure the good value remains unchanged
    assert result == 1234
    assert config_reader.content.get('RockSniffer', 'port') == initial_value

# Invalid boolean values are currently treated as False by strtobool().
# Error logging and automatic recovery will need separate tests if
# strict boolean validation is introduced.
def test_invalid_bool_value_returns_false(config_reader):
    # Currently, unrecognized boolean values are treated as False.
    config_reader.content.set(
        'RockSniffer', 'enabled', 'not_a_bool'
    )

    result = config_reader.get_bool('RockSniffer', 'enabled')

    assert result is False
    assert config_reader.content.get(
        'RockSniffer', 'enabled'
    ) == 'not_a_bool'


# Saving Configuration Test
def test_save_config(config_reader):
    # Set an invalid value to trigger automatic recovery and saving
    config_reader.content.set('RockSniffer', 'port', 'invalid')

    # Trigger configuration recovery
    result = config_reader.get('RockSniffer', 'port', int)

    # Reload the config and verify that the corrected value was saved
    new_reader = ConfigReader(config_reader.config_file_path)

    assert result == 1234
    assert new_reader.get_int_value('RockSniffer', 'port') == 1234


# Error Handling in the `get` Method Test
def test_get_method_error_handling(config_reader):
    # Set a bad value to trigger error handling
    config_reader.content.set('RockSniffer', 'port', 'bad_value')

    # Capture the log output
    with patch('config.config_reader.log') as mock_log:
        result = config_reader.get('RockSniffer', 'port', int)

        # Verify that the error was logged
        mock_log.error.assert_called_with(
            'Error retrieving value from %s for section [%s] with key [%s].',
            config_reader.config_abspath, 'RockSniffer', 'port'
        )

    # Verify that the invalid value was replaced with the default
    assert result == 1234
    assert config_reader.content.get('RockSniffer', 'port') == '1234'


# Ensuring Configuration Directory Creation Test
def test_create_directory(mock_file_utils, config_file_path):
    ConfigReader(config_file_path)
    mock_file_utils.assert_called_once_with(os.path.dirname(config_file_path))


# Correct Configuration File Path Test
def test_config_file_path(config_file_path):
    reader = ConfigReader(config_file_path)
    assert reader.config_abspath == os.path.abspath(config_file_path)
