#!/usr/bin/env python

import codecs
import logging
import os
import struct
import sys
import zlib

from Crypto.Cipher import AES

from utils import file_utils

log = logging.getLogger()

DIR_PSARC_INFO_FILES = '../psarc-info-files'
EXTENSION_PSARC_INFO_JSON = '.info.json'

ENTRY_SIZE = 30
BLOCK_SIZE = 65536

ARC_KEY = 'C53DB23870A1A2F71CAE64061FDD0E1157309DC85204D4C5BFDF25090DF2572C'
ARC_IV = 'E915AA018FEF71FC508132E4BB4CEB42'


def pad(data, blocksize=16):
    """Zeros padding"""
    # So we need zeroes in order to match AES's encoding scheme which breaks
    # the data into 16-byte chunks. If we have 52 bytes to decode, then we have
    # 3 full 16-byte blocks, and 4 left over. This means we need 12 bytes worth
    # of padding. That means we get 12 bytes worth of zeroes.
    padding = (blocksize - len(data)) % blocksize
    # Modify this to return a bytes object, since that's what pycrypto needs.
    return data + bytes(padding)


def stdout_same_line(line):
    """Prepend carriage return and output to stdout"""
    sys.stdout.write('\r' + line[:80])
    sys.stdout.flush()


def read_entry(filestream, entry):
    """Extract zlib for one entry"""
    data = bytes()

    length = entry['length']
    zlength = entry['zlength']
    filestream.seek(entry['offset'])

    i = 0
    while len(data) < length:
        if zlength[i] == 0:
            data += filestream.read(BLOCK_SIZE)
        else:
            chunk = filestream.read(zlength[i])
            try:
                data += zlib.decompress(chunk)
            except zlib.error:
                data += chunk
        i += 1

    return data


def cipher_toc():
    """AES CFB Mode"""
    return AES.new(codecs.decode(ARC_KEY, 'hex'), mode=AES.MODE_CFB,
                   IV=codecs.decode(ARC_IV, 'hex'), segment_size=128)


def read_toc(filestream):
    """Read entry list and Z-fragments.
    Returns a list of entries to be used with read_entry."""

    entries = []
    zlength = []

    filestream.seek(0)
    header = struct.unpack('>4sL4sLLLLL', filestream.read(32))

    toc_size = header[3] - 32
    n_entries = header[5]
    toc = cipher_toc().decrypt(pad(filestream.read(toc_size)))
    toc_position = 0

    idx = 0
    while idx < n_entries:
        data = toc[toc_position:toc_position + ENTRY_SIZE]

        entries.append({
            'md5': data[:16],
            'zindex': struct.unpack('>L', data[16:20])[0],
            'length': struct.unpack('>Q', b'\x00' * 3 + data[20:25])[0],
            'offset': struct.unpack('>Q', b'\x00' * 3 + data[25:])[0]
        })
        toc_position += ENTRY_SIZE
        idx += 1

    idx = 0
    while idx < (toc_size - ENTRY_SIZE * n_entries) / 2:
        data = toc[toc_position:toc_position + 2]
        zlength.append(struct.unpack('>H', data)[0])
        toc_position += 2
        idx += 1

    for entry in entries:
        entry['zlength'] = zlength[entry['zindex']:]

    # Process the first entry as it contains the file listing
    entries[0]['filepath'] = ''
    filepaths = read_entry(filestream, entries[0]).split()
    for entry, filepath in zip(entries[1:], filepaths):
        entry['filepath'] = filepath.decode("utf-8")

    # TODO return only the useful files
    return entries[1:]


def extract_psarc(filename_to_extract):
    base_path = os.path.join(DIR_PSARC_INFO_FILES, os.path.basename(filename_to_extract)[:-6])
    # base_path2 = os.path.join(DIR_PSARC_INFO_FILES)
    # TODO extract this create dir to the module __init__ where the function is called
    file_utils.create_directory(os.path.join(DIR_PSARC_INFO_FILES))

    with open(filename_to_extract, 'rb') as psarc:
        entries = read_toc(psarc)
        # TODO use different log but in debug level
        log.info('Extracting ', os.path.basename(filename_to_extract))

        for idx, entry in enumerate(entries):
            filepath_from_the_entry = entry['filepath']
            if is_song_info_file(filepath_from_the_entry):
                write_info_file(entry, filename_to_extract, psarc)


def write_info_file(entry, filename_to_extract, psarc):
    json_filename = filename_to_extract + EXTENSION_PSARC_INFO_JSON
    json_file_path = os.path.join(DIR_PSARC_INFO_FILES, os.path.basename(json_filename))
    data = read_entry(psarc, entry)
    with open(json_file_path, 'wb') as fstream:
        log.info('Writing ', json_file_path)
        fstream.write(data)


def create_dir_if_not_exists(base_path):
    if not os.path.exists(base_path):
        os.makedirs(base_path)


def is_song_info_file(file_name):
    # TODO remove unused
    # return True
    # TODO keep only one file what is used later on
    return file_name.find('.hsan') > -1
    # return file_name.find('manifests/songs_dlc') > -1 and file_name.find('.hsan') > -1
    # return file_name.find('songs/arr') > -1 or file_name.find('manifests/songs_dlc') > -1


if __name__ == '__main__':
    psarc_files = ('c:\\work\\PycharmProjects\\Rocksmith-Servant\\tmp\\AC-DC_Big-Gun_v3_5_DD_p.psarc',
                   'c:\\work\\PycharmProjects\\Rocksmith-Servant\\tmp\\BABYMETAL_ONE-(English)_v1_4_p.psarc')
    for psarc_file in psarc_files:
        extract_psarc(psarc_file)
