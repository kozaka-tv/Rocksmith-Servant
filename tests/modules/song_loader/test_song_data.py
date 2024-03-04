from modules.song_loader.song_data import SongData


def test_song_data__when_no_input_in_constructor__then_everything_is_empty():
    song_data = SongData()
    assert song_data is not None
    assert song_data.rspl_request_id is None
    assert song_data.rspl_song_id is None
    assert song_data.cdlc_id is None
    assert song_data.artist is None
    assert song_data.title is None
    assert song_data.artist_title is None
    assert song_data.rspl_official is None
    assert song_data.rspl_position is None
    assert song_data.song_file_name is None
    # TODO do we need this state at all?
    # assert song_data.state is NEW_REQUEST
    assert len(song_data.tags) is 0
    assert song_data.found_in_db is False
    assert song_data.loaded_under_the_game is False
    assert song_data.missing is False


def test_song_data__when_only_artist_is_given__then_artist_and_title_is_none():
    song_data = SongData(artist="My Artist")
    assert song_data.artist_title is None


def test_song_data__when_only_title_is_given__then_artist_and_title_is_none():
    song_data = SongData(title="My Title")
    assert song_data.artist_title is None


def test_song_data__when_artist_and_title_is_given__then_artist_and_title_is_set():
    song_data = SongData(artist="My Artist", title="My Title")
    assert song_data.artist_title == 'My Artist - My Title'


def test_is_official__when_no_official_is_set__then_return_false():
    song_data = SongData()
    assert song_data.is_official is False


def test_is_official__when_rspl_official_is_minus_1__then_return_false():
    song_data = SongData()
    song_data.rspl_official = -1
    assert song_data.is_official is False


def test_is_official__when_rspl_official_is_3__then_return_true():
    song_data = SongData()
    song_data.rspl_official = 3
    assert song_data.is_official is True


def test_is_official__when_rspl_official_is_4__then_return_true():
    song_data = SongData()
    song_data.rspl_official = 4
    assert song_data.is_official is True

# def test_is_missing():
#     assert False
