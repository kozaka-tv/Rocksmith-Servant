create table songs
(
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
    dlc_id
);

create index idx_artist_title
    on songs (colArtist, colTitle);

create index idx_file_name
    on songs (colFileName);
