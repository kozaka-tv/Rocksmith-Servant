create table if not exists songs
(
    id                      integer not null
        constraint songs_pk
            primary key autoincrement,
    rowId                   text,
    colArtist               text,
    colTitle                text,
    colAlbum                text,
    colKey                  text,
    colArrangements         text,
    colTunings              text,
    colSongLength           text,
    colRepairStatus         text,
    colSongYear             text,
    colSongVolume           text,
    colFileName             text,
    colFileDate             text,
    colAppID                text,
    colPackageAuthor        text,
    colPackageVersion       text,
    colTagged               text,
    colIgnitionID           text,
    colIgnitionDate         text,
    colIgnitionVersion      text,
    colIgnitionAuthor       text,
    colArtistTitleAlbum     text,
    colArtistTitleAlbumDate text,
    colArtistSort,
    dlc_id,
    artistNormalized        text,
    titleNormalized         text
);

create index if not exists songs_artist_title_index
    on songs (colArtist, colTitle);

create index if not exists songs_artist_title_normalized_index
    on songs (artistNormalized, titleNormalized);

create index if not exists songs_file_name_index
    on songs (colFileName);

create unique index if not exists songs_id_index
    on songs (id);

