from operator import eq

from modules.song_loader.song_data import SongData

ID = 666
ARTIST = "My Artist"
TITLE = "My Title"
SONG_FILE_NAME = "my_super_song.psarc"


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
    assert len(song_data.tags) == 0
    assert song_data.found_in_db is False
    assert song_data.loaded_under_the_game is False
    assert song_data.missing is False


def test_song_data__when_rspl_request_id_is_given__then_rspl_request_id_is_set():
    song_data = SongData(rspl_request_id=ID)
    assert song_data.rspl_request_id == ID


def test_song_data__when_cdlc_id_is_given__then_cdlc_id_is_set():
    song_data = SongData(cdlc_id=ID)
    assert song_data.cdlc_id == ID


def test_song_data__when_rspl_song_id_is_given__then_rspl_song_id_is_set():
    song_data = SongData(rspl_song_id=ID)
    assert song_data.rspl_song_id == ID


def test_song_data__when_artist_is_given__then_artist_is_set():
    song_data = SongData(artist=ARTIST)
    assert song_data.artist == ARTIST


def test_song_data__when_title_is_given__then_title_is_set():
    song_data = SongData(title=TITLE)
    assert song_data.title == TITLE


def test_song_data__when_song_file_name_is_given__then_song_file_name_is_set():
    song_data = SongData(song_file_name=SONG_FILE_NAME)
    assert song_data.song_file_name == SONG_FILE_NAME


def test_song_data__when_only_artist_is_given__then_artist_and_title_is_none():
    song_data = SongData(artist=ARTIST)
    assert song_data.artist_title is None


def test_song_data__when_only_title_is_given__then_artist_and_title_is_none():
    song_data = SongData(title=TITLE)
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


def test_is_missing__when_not_missing__then_return_false():
    song_data = SongData()
    song_data.missing = False
    assert song_data.is_missing is False


def test_is_missing__when_missing__then_return_true():
    song_data = SongData()
    song_data.missing = True
    assert song_data.is_missing is True


# TODO
# def test__eq__():
#     assert False


# TODO
# def test__hash__():
#     assert False


def test__ref__():
    song_data = SongData()
    song_data.rspl_request_id = 1
    song_data.rspl_song_id = 2
    song_data.cdlc_id = 3
    song_data.artist = ARTIST
    song_data.title = TITLE
    song_data.artist_title = ARTIST + " - " + TITLE
    song_data.rspl_official = True
    song_data.song_file_name = SONG_FILE_NAME
    song_data.missing = True

    assert eq(str(song_data),
              '<SongData: '
              'rspl_request_id=1, '
              'rspl_song_id=2, '
              'cdlc_id=3, '
              'artist=My Artist, '
              'title=My Title, '
              'artist_title=My Artist - My Title, '
              'rspl_official=True, '
              'song_file_name=my_super_song.psarc, '
              'missing=True'
              '>'
              )
