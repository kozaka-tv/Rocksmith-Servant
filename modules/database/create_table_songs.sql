create table if not exists songs
(
    id                   integer not null
        constraint songs_pk
            primary key autoincrement,
    rowId                text,
    artist               text,
    title                text,
    album                text,
    key                  text,
    arrangements         text,
    tunings              text,
    songLength           text,
    repairStatus         text,
    songYear             text,
    songVolume           text,
    fileName             text unique,
    fileDate             text,
    appID                text,
    packageAuthor        text,
    packageVersion       text,
    tagged               text,
    ignitionID           text,
    ignitionDate         text,
    ignitionVersion      text,
    ignitionAuthor       text,
    artistTitleAlbum     text,
    artistTitleAlbumDate text,
    artistSort,
    dlc_id,
    artistNormalized     text,
    titleNormalized      text
);

create index if not exists songs_artist_title_index
    on songs (artist, title);

create index if not exists songs_artist_title_normalized_index
    on songs (artistNormalized, titleNormalized);

create index if not exists songs_file_name_index
    on songs (fileName);

create unique index if not exists songs_id_index
    on songs (id);

