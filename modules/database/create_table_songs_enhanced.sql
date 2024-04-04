create table if not exists songs_enhanced
(
    id                      integer not null
        constraint songs_enhanced_pk
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

create index if not exists songs_enhanced_artist_title_index
    on songs_enhanced (colArtist, colTitle);

create index if not exists songs_enhanced_artist_title_normalized_index
    on songs_enhanced (artistNormalized, titleNormalized);

create index if not exists songs_enhanced_file_name_index
    on songs_enhanced (colFileName);

create unique index if not exists songs_enhanced_id_index
    on songs_enhanced (id);
