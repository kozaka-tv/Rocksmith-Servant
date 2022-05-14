import os


class SongData:
    def __init__(self, sr_id, cdlc_id, song_file_name):
        self.sr_id = sr_id
        self.cdlc_id = cdlc_id
        self.song_file_name = song_file_name

    # TODO sr_id? or cdlc_id? or something else?
    def __eq__(self, other):
        return self.sr_id == other.sr_id

    def __hash__(self):
        return hash(self.sr_id)

    def __repr__(self):
        return os.linesep + '<SongData: sr_id={}, cdlc_id={}, song_file_name={}>'.format(self.sr_id,
                                                                                         self.cdlc_id,
                                                                                         self.song_file_name)


# TODO remove this later if the eq is decided!
s1 = SongData(1, 555, 'asd')
s2 = SongData(2, 666, 'qwe')
s3 = SongData(1, 777, '123')

song_data_set = {s1, s2, s3}
print(song_data_set)
# output: {<Person tom>, <Person mary>}
