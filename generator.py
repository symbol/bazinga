#!/usr/bin/env python3

import argparse
import os
from pathlib import Path

from NodeConfigurator import NodeConfigurator


def main():
    parser = argparse.ArgumentParser(description='Node configurator generator')
    parser.add_argument('--mode', help='node type', choices=('api', 'peer', 'dual'), required=True)
    parser.add_argument('--voting', help='node will be voting', action='store_true')
    parser.add_argument('--harvesting', help='node will be harvesting', action='store_true')
    parser.add_argument('--output', help='output directory', default='..')
    parser.add_argument('--force', help='overwrite output directory', action='store_true')
    args = parser.parse_args()

    if not Path(args.output).is_dir():
        os.makedirs(args.output, mode=0o700)

    configurator = NodeConfigurator(args.output, args.force, args.mode, args.voting, args.harvesting)
    configurator.check_requirements()
    configurator.prepare_resources()
    configurator.prepare_peers()
    configurator.prepare_startup_files()


if __name__ == '__main__':
    main()
