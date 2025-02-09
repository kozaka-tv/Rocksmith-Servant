# tests/test_song_loader_helper.py

from modules.servant.song_loader.song_loader_helper import playlist_does_not_changed


def test_playlist_does_not_change_identical_sets():
    rsplaylist_request_strings = {"song1", "song2", "song3"}
    new_rsplaylist_request_strings = {"song1", "song2", "song3"}
    assert playlist_does_not_changed(rsplaylist_request_strings, new_rsplaylist_request_strings) is True


def test_playlist_does_not_change_identical_sets_different_order():
    rsplaylist_request_strings = {"song1", "song2", "song3"}
    new_rsplaylist_request_strings = {"song2", "song1", "song3"}
    assert playlist_does_not_changed(rsplaylist_request_strings, new_rsplaylist_request_strings) is True


def test_playlist_changes_differing_sets():
    rsplaylist_request_strings = {"song1", "song2", "song3"}
    new_rsplaylist_request_strings = {"song1", "song2", "song4"}
    assert playlist_does_not_changed(rsplaylist_request_strings, new_rsplaylist_request_strings) is False


def test_playlist_changes_differing_sets_less_new():
    rsplaylist_request_strings = {"song1", "song2", "song3"}
    new_rsplaylist_request_strings = {"song1", "song2"}
    assert playlist_does_not_changed(rsplaylist_request_strings, new_rsplaylist_request_strings) is False


def test_playlist_changes_differing_sets_more_new():
    rsplaylist_request_strings = {"song1", "song2"}
    new_rsplaylist_request_strings = {"song1", "song2", "song3"}
    assert playlist_does_not_changed(rsplaylist_request_strings, new_rsplaylist_request_strings) is False


def test_playlist_changes_empty_vs_non_empty():
    rsplaylist_request_strings = set()
    new_rsplaylist_request_strings = {"song1", "song2", "song3"}
    assert playlist_does_not_changed(rsplaylist_request_strings, new_rsplaylist_request_strings) is False


def test_playlist_changes_non_empty_vs_empty():
    rsplaylist_request_strings = {"song1", "song2", "song3"}
    new_rsplaylist_request_strings = set()
    assert playlist_does_not_changed(rsplaylist_request_strings, new_rsplaylist_request_strings) is False


def test_playlist_does_not_change_both_empty():
    rsplaylist_request_strings = set()
    new_rsplaylist_request_strings = set()
    assert playlist_does_not_changed(rsplaylist_request_strings, new_rsplaylist_request_strings) is True
