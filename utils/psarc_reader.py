#!/usr/bin/env python

import codecs
import json
import logging
import os
import struct
import zlib

from Crypto.Cipher import AES

from definitions import PSARC_INFO_FILE_CACHE_DIR, EXT_PSARC_INFO_JSON
from modules.song_loader.song_data import SongData
from utils import file_utils
from utils.exceptions import ExtractError

log = logging.getLogger()

ENTRY_SIZE = 30
BLOCK_SIZE = 65536

ARC_KEY = 'C53DB23870A1A2F71CAE64061FDD0E1157309DC85204D4C5BFDF25090DF2572C'
ARC_IV = 'E915AA018FEF71FC508132E4BB4CEB42'

ATTR_ARTIST_NAME = 'ArtistName'
ATTR_SONG_NAME = 'SongName'


def extract(filename_to_extract, song_data_input, write_to_file=False):
    log.debug('Extracting %s', filename_to_extract)

    if log.isEnabledFor(logging.DEBUG) or write_to_file:
        file_utils.create_directory_logged(PSARC_INFO_FILE_CACHE_DIR)

    with open(filename_to_extract, 'rb') as psarc:
        entry = __get_psarc_info(psarc)
        if entry is None:
            log.error('Could not extract any song information from the psarc file: %s', filename_to_extract)
            return

        if log.isEnabledFor(logging.DEBUG) or write_to_file:
            __write_info_file(entry, filename_to_extract, psarc)

        __create_song_data(entry, psarc, song_data_input)
        log.debug("Song data with the extracted information: %s", song_data_input)


def __create_song_data(entry, psarc, song_data_input: SongData):
    song_data_dict = __get_song_data_dict(entry, psarc)

    iterator = iter(song_data_dict['Entries'])

    while key := next(iterator):
        log.debug("Extracting attribute from the entry: %s", key)

        attributes = song_data_dict['Entries'][key]['Attributes']
        artist_name = __get_artist_name(attributes, key, song_data_dict)
        if artist_name is not None:
            song_data_input.artist = artist_name
            song_data_input.title = __get_song_name(attributes, song_data_dict)
            return

    raise ExtractError(f"Could not extract useful attribute information from: {song_data_dict}")


def __get_song_data_dict(entry, psarc):
    data = __read_entry_data(psarc, entry).decode('utf-8').replace('\\r\\n', '')
    return json.loads(data)


def __get_artist_name(attributes_, key, song_data_dict):
    try:
        return attributes_[ATTR_ARTIST_NAME]
    except KeyError:
        log.debug("Could not extract attribute %s from the entry: %s - %s", ATTR_ARTIST_NAME, key, song_data_dict)
        return None


def __get_song_name(attributes_, song_data_dict):
    try:
        return attributes_[ATTR_SONG_NAME]
    except KeyError:
        log.error("Could not extract attribute %s from this entry: %s", ATTR_SONG_NAME, song_data_dict)
        return None


def __pad(data, blocksize=16):
    """Zeros padding"""
    # So we need zeroes in order to match AES's encoding scheme which breaks
    # the data into 16-byte chunks. If we have 52 bytes to decode, then we have
    # 3 full 16-byte blocks, and 4 left over. This means we need 12 bytes worth
    # of padding. That means we get 12 bytes worth of zeroes.
    padding = (blocksize - len(data)) % blocksize
    # Modify this to return a bytes object, since that's what pycrypto needs.
    return data + bytes(padding)


def __read_entry_data(filestream, entry):
    """Extract zlib for one entry"""
    data = bytes()

    length = entry['length']
    z_length = entry['zlength']
    filestream.seek(entry['offset'])

    i = 0
    while len(data) < length:
        if z_length[i] == 0:
            data += filestream.read(BLOCK_SIZE)
        else:
            chunk = filestream.read(z_length[i])
            try:
                data += zlib.decompress(chunk)
            except zlib.error:
                data += chunk
        i += 1

    return data


def __cipher_toc():
    """AES CFB Mode"""
    return AES.new(codecs.decode(ARC_KEY, 'hex'), mode=AES.MODE_CFB, IV=codecs.decode(ARC_IV, 'hex'), segment_size=128)


def __get_psarc_info(filestream):
    """Read entry list and Z-fragments.
    Returns a list of entries to be used with read_entry."""

    entries = []
    z_length = []

    filestream.seek(0)
    header = struct.unpack('>4sL4sLLLLL', filestream.read(32))

    toc_size = header[3] - 32
    n_entries = header[5]
    toc = __cipher_toc().decrypt(__pad(filestream.read(toc_size)))
    toc_position = 0

    idx = 0
    while idx < n_entries:
        data = toc[toc_position:toc_position + ENTRY_SIZE]

        entries.append({  # 'md5': data[:16],
            'zindex': struct.unpack('>L', data[16:20])[0], 'length': struct.unpack('>Q', b'\x00' * 3 + data[20:25])[0],
            'offset': struct.unpack('>Q', b'\x00' * 3 + data[25:])[0]})
        toc_position += ENTRY_SIZE
        idx += 1

    idx = 0
    while idx < (toc_size - ENTRY_SIZE * n_entries) / 2:
        data = toc[toc_position:toc_position + 2]
        z_length.append(struct.unpack('>H', data)[0])
        toc_position += 2
        idx += 1

    for entry in entries:
        entry['zlength'] = z_length[entry['zindex']:]

    # Process the first entry as it contains the file listing
    entries[0]['filepath'] = ''
    filepaths = __read_entry_data(filestream, entries[0]).split()
    for entry, filepath in zip(entries[1:], filepaths):
        filepath_decoded = filepath.decode("utf-8")
        if __is_song_info_file(filepath_decoded):
            entry['filepath'] = filepath_decoded
            return entry

    return None


def __write_info_file(entry, filename_to_extract, psarc):
    json_filename = filename_to_extract + EXT_PSARC_INFO_JSON
    info_file_json_path = os.path.join(PSARC_INFO_FILE_CACHE_DIR, os.path.basename(json_filename))
    data_to_write = __read_entry_data(psarc, entry)
    with open(info_file_json_path, 'wb') as fstream:
        fstream.write(data_to_write)
        log.debug('Info file %s created.', info_file_json_path)


def __is_song_info_file(file_name):
    return file_name.find('.hsan') > -1
