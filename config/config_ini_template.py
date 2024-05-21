serialized = {
    "RockSniffer": {
        "enabled": False,
        "host": "localhost",
        "port": "9938",
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
        "cdlc_dir": "import",
        "rspl_tag_to_download": "<Create a tag in RS Playlist for song need to be downloaded and enter to here>",
        "rspl_tag_downloaded": "<Create a tag in RS Playlist for song which has been downloaded and enter to here>",
        "rspl_tag_loaded": "<Create a tag in RS Playlist for song loaded under RS and enter to here>",
        "rspl_tag_new_viewer_request": "<Create a tag in RS Playlist for song which one has been requested by a "
                                       "new viewer and enter to here>",
        "rspl_tag_raider_request": "<Create a tag in RS Playlist for song which one has been requested by a "
                                   "raider streamer and enter to here>",
        "rspl_tag_vip_viewer_request": "<Create a tag in RS Playlist for song which one has been requested by a "
                                       "channel VIP viewer and enter to here>",
        "cfsm_file_name": "SongsMasterGrid.json",
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
