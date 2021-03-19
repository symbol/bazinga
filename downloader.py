import os
from hashlib import sha3_512

import requests
from zenlog import log


def calculate_buffer_hash(buffer):
    hasher = sha3_512()
    hasher.update(buffer)
    return hasher.hexdigest().upper()


def calculate_file_hash(filepath):
    with open(filepath, 'rb') as input_file:
        return calculate_buffer_hash(input_file.read())


def download_file(output_dir, descriptor):
    output_path = output_dir / descriptor['name']

    if output_path.is_file():
        if descriptor['hash'] == calculate_file_hash(output_path):
            log.info('proper file already downloaded ({})'.format(descriptor['name']))
            return

        log.warn('file exists, but has invalid hash, re-downloading')
        os.remove(output_path)

    req = requests.get(descriptor['url'])
    if 200 != req.status_code:
        raise RuntimeError('could not download file ({}), try again'.format(descriptor['name']))

    if descriptor['hash'] != calculate_buffer_hash(req.content):
        raise RuntimeError('downloaded file ({}) has invalid hash'.format(descriptor['name']))

    with open(output_path, 'wb') as output_file:
        output_file.write(req.content)
