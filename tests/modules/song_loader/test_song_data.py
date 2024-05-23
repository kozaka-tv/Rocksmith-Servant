from modules.song_loader.song_data import SongData

SONG_FILENAME = "my_super_song.psarc"

ARTIST = "My Artist"
TITLE = "My Title"
ARTIST_TITLE = 'My Artist - My Title'

RSPL_REQUEST_ID = 1
CDLC_ID = 3
RSPL_SONG_ID = 666
OFFICIAL = True
RSPL_POSITION = 4

TAGS = {'tag1', 'tag2'}


def test_song_data__when_no_input_in_constructor__then_everything_is_empty():
    song_data = SongData()

    assert song_data is not None

    assert song_data.song_filename is None

    assert song_data.artist is None
    assert song_data.title is None
    assert song_data.artist_title is None

    assert song_data.rspl_request_id is None
    assert song_data.cdlc_id is None
    assert song_data.rspl_song_id is None
    assert song_data.rspl_official is None
    assert song_data.rspl_position is None

    assert len(song_data.tags) == 0


def test_song_data__when_song_filename_is_given__then_song_filename_is_set():
    song_data = SongData(song_filename=SONG_FILENAME)
    assert song_data.song_filename == SONG_FILENAME


def test_song_data__when_artist_is_given__then_artist_is_set():
    song_data = SongData(artist=ARTIST)
    assert song_data.artist == ARTIST


def test_song_data__when_title_is_given__then_title_is_set():
    song_data = SongData(title=TITLE)
    assert song_data.title == TITLE


def test_song_data__when_only_artist_is_given__then_artist_and_title_is_none():
    song_data = SongData(artist=ARTIST)
    assert song_data.artist_title is None


def test_song_data__when_only_title_is_given__then_artist_and_title_is_none():
    song_data = SongData(title=TITLE)
    assert song_data.artist_title is None


def test_song_data__when_artist_and_title_is_given__then_artist_and_title_is_set():
    song_data = SongData(artist="My Artist", title="My Title")
    assert song_data.artist_title == ARTIST_TITLE


def test_song_data__when_rspl_request_id_is_given__then_rspl_request_id_is_set():
    song_data = SongData(rspl_request_id=RSPL_REQUEST_ID)
    assert song_data.rspl_request_id == RSPL_REQUEST_ID


def test_song_data__when_cdlc_id_is_given__then_cdlc_id_is_set():
    song_data = SongData(cdlc_id=CDLC_ID)
    assert song_data.cdlc_id == CDLC_ID


def test_song_data__when_rspl_song_id_is_given__then_rspl_song_id_is_set():
    song_data = SongData(rspl_song_id=RSPL_SONG_ID)
    assert song_data.rspl_song_id == RSPL_SONG_ID


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
    assert song_data.is_official is OFFICIAL


def test_is_official__when_rspl_official_is_4__then_return_true():
    song_data = SongData()
    song_data.rspl_official = 4
    assert song_data.is_official is OFFICIAL


def test_rspl_position__when_rspl_position_is_set__then_return_rspl_position():
    song_data = SongData()
    song_data.rspl_position = RSPL_POSITION
    assert song_data.rspl_position == RSPL_POSITION


def test_tags__when_tags_is_set__then_return_tags():
    song_data = SongData()
    song_data.tags = TAGS
    assert song_data.tags == TAGS


def test__ref__():
    song_data = SongData()

    song_data.song_filename = SONG_FILENAME

    song_data.artist = ARTIST
    song_data.title = TITLE
    song_data.artist_title = ARTIST + " - " + TITLE

    song_data.rspl_request_id = RSPL_REQUEST_ID
    song_data.cdlc_id = CDLC_ID
    song_data.rspl_song_id = RSPL_SONG_ID
    song_data.rspl_official = OFFICIAL
    song_data.rspl_position = RSPL_POSITION

    song_data.tags = TAGS

    actual = str(song_data)

    assert (actual == ('<SongData: song_filename=my_super_song.psarc, artist=My Artist, title=My '
                       'Title, artist_title=My Artist - My Title, rspl_request_id=1, cdlc_id=3, '
                       "rspl_song_id=666, rspl_official=True, rspl_position=4, tags={'tag2', "
                       "'tag1'}>")
            or actual == ('<SongData: song_filename=my_super_song.psarc, artist=My Artist, title=My '
                          'Title, artist_title=My Artist - My Title, rspl_request_id=1, cdlc_id=3, '
                          "rspl_song_id=666, rspl_official=True, rspl_position=4, tags={'tag1', "
                          "'tag2'}>"))
