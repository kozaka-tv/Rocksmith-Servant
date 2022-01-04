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
        "allow_load_when_in_game": True,
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
