serialized = {
    "RockSniffer": {
        "enabled": False,
        "host": "localhost",
        "port": "9938",
    },
    "SetlistLogger": {
        "enabled": False,
        "setlist_path": "<Enter Your Directory where do you want to have your Setlist>",
    },
    "SongLoader": {
        "enabled": False,
        "cdlc_dir": "import",
        "cfsm_file_name": "SongsMasterGrid.json",
        "cdlc_archive_dir": "<Enter your CDLC archive directory, where you store all of your downloaded CDLCs>",
        "rocksmith_cdlc_dir": "<Enter your Rocksmith CDLC directory, where you have all the loaded CDLC songs>",
        "allow_load_when_in_game": True,
        "phpsessid": "<Enter your PHP Session ID from the cookie of the RS Playlist after login>"
    },
    "SceneSwitcher": {
        "enabled": False,
    },
    "FileManager": {
        "enabled": False,
        "source_directories": "<Enter source directories (separated by ';') from where do you want to move CDLC files>",
        "destination_directory": "<Enter Your Directory to where do you want to move CDLC files>",
        "using_cfsm": False,
    },
    "OBSWebSocket": {
        "host": "localhost",
        "port": 4444,
        "pass": "",
    },
    "Behaviour": {
        "cooldown": 3,
        "paused": "<PauseSceneName>",
        "in_game": "<InGameSceneName>",
        "in_menu": "<MenuSceneName>",
        "forbidden_switch_on_scenes": "<IntroSceneName; OutroSceneName>",
    },
    "Debugging": {
        "debug": False,
        "debug_log_interval": 1
    }
}
