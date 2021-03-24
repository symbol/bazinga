import argparse
import asyncio
import os
import stat
from collections import Counter
from pathlib import Path

import aiohttp
from aiohttp import ClientSession
from symbolchain.core.CryptoTypes import PrivateKey
from symbolchain.core.sym.KeyPair import KeyPair
from symbolchain.core.sym.VotingKeysGenerator import VotingKeysGenerator
from zenlog import log

from nodes import nodes


async def fetch_html(url, session, **kwargs):
    resp = await session.request(method='GET', url=url, **kwargs)
    resp.raise_for_status()
    log.info('Got response [{}] for URL: {}'.format(resp.status, url))
    data = await resp.json()
    return data


async def parse(url, session, collected):
    try:
        data = await fetch_html(url, session)
        collected[url] = data
    except (aiohttp.ClientError, aiohttp.http_exceptions.HttpProcessingError) as exc:
        log.error('aiothtp exception for {} [{}]: {}'.format(url, getattr(exc, 'status', None), getattr(exc, 'message', None)))
    except Exception as exc:  # pylint: disable=broad-except
        log.error('Non-aiohttp exception occured: {}'.format(getattr(exc, '__dict__', {})))


async def get(urls, epoch_descriptor):
    collected = {}
    async with ClientSession() as session:
        tasks = map(lambda url: parse(url, session, collected), urls)
        await asyncio.gather(*tasks)

    counter = Counter(map(lambda e: e['latestFinalizedBlock']['finalizationEpoch'], collected.values()))
    epoch_descriptor['most_common'] = counter.most_common(1)[0][0]


def toUrl(node):
    return 'http://{}:3000/chain/info'.format(node)


def generate_voting_key_file(filepath, start_epoch, epoch_range):
    key_pair = KeyPair(PrivateKey.random())
    voting_keys_generator = VotingKeysGenerator(key_pair)
    end_epoch = start_epoch + epoch_range
    voting_key_buffer = voting_keys_generator.generate(start_epoch, end_epoch)
    log.info('voting key start epoch: {}, end epoch: {}'.format(start_epoch, end_epoch))
    log.info('voting key root public key: {}'.format(key_pair.public_key))

    # create the file
    with open(filepath, 'wb') as output_file:
        pass

    os.chmod(filepath, stat.S_IRUSR + stat.S_IWUSR)

    with open(filepath, 'w+b') as output_file:
        output_file.write(voting_key_buffer)


def main():
    parser = argparse.ArgumentParser(description='Voting key tool wrapper')
    parser.add_argument('--filename', help='voting key filename', default='private_key_tree1.dat')
    parser.add_argument('--start-epoch', help='start epoch, if 0, retrive current epoch by querying online nodes', type=int, default=0)
    parser.add_argument(
        '--range',
        help='total range of epochs (112-360)',
        metavar='epoch_range',
        type=int,
        required=True,
        choices=range(112, 361))
    parser.add_argument('--force', help='overwrite output file if it already exists', action='store_true')
    args = parser.parse_args()

    filepath = Path(os.getcwd()) / args.filename
    if filepath.exists() and not args.force:
        raise FileExistsError('output file ({}) already exists, use --force to overwrite'.format(filepath))

    start_epoch = args.start_epoch
    if 0 == start_epoch:
        urls = set(map(toUrl, nodes))
        epoch = {'most_common': 1}
        asyncio.run(get(urls, epoch))
        start_epoch = epoch['most_common']
        log.info('---- ' * 15)

    generate_voting_key_file(filepath, start_epoch, args.range)


if __name__ == '__main__':
    main()
