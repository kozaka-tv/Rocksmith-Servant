create table main.songs
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

create index main.songs_artist_title_index
    on main.songs (colArtist, colTitle);

create index main.songs_artist_title_normalized_index
    on main.songs (artistNormalized, titleNormalized);

create index main.songs_file_name_index
    on main.songs (colFileName);

create unique index main.songs_id_index
    on main.songs (id);

