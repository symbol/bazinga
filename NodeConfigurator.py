import json
import os
import random
import shutil
from pathlib import Path

from zenlog import log

from compose import patch_compose
from patcher import patch_config
from settings import HARVESTING_KEY_FILENAME, VRF_KEY_FILENAME, node_settings, role_settings


def to_short_name(filename):
    return filename.name[len('config-'):-len('.properties')]


def select_random_peers(source, destination, count):
    all_nodes = None
    with open(source, 'r') as input_file:
        all_nodes = json.load(input_file)

    random.shuffle(all_nodes['knownPeers'])
    num_nodes = min(len(all_nodes['knownPeers']), count)
    all_nodes['knownPeers'] = all_nodes['knownPeers'][:num_nodes]

    with open(destination, 'w') as output_file:
        json.dump(all_nodes, output_file, indent=4)


class NodeConfigurator:
    def __init__(self, output_directory, force_output, node_mode, is_voting, is_harvesting):  # pylint: disable=too-many-arguments
        self.templates = Path(__file__).parent / 'templates'
        self.dir = Path(output_directory)
        self.force_dir = force_output
        self.mode = node_mode

        self.is_voting = is_voting
        self.is_harvesting = is_harvesting

        self.has_harvesting_key = Path(HARVESTING_KEY_FILENAME).is_file()
        self.has_vrf_key = Path(VRF_KEY_FILENAME).is_file()

    def check_requirements(self):
        if not self.is_harvesting:
            return

        if not self.has_harvesting_key:
            raise RuntimeError('harvesting requested, but harvesting key file ({}) does not exist'.format(HARVESTING_KEY_FILENAME))

        if not self.has_vrf_key:
            raise RuntimeError('harvesting requested, but vrf key file ({}) does not exist'.format(VRF_KEY_FILENAME))

    def prepare_resources(self):
        log.info('preparing base settings')
        destination = self.dir / 'resources'
        if destination.is_dir():
            if self.force_dir:
                shutil.rmtree(destination)
            else:
                raise FileExistsError('output directory already exists, use --force to overwrite')

        self._copy_and_patch_resources(destination)

        if self.is_harvesting:
            log.info('turning on harvesting')
            self.run_patches(node_settings['harvesting'])

        if self.is_voting:
            log.info('turning on voting')
            self.run_patches(node_settings['voting'])

    def _copy_and_patch_resources(self, destination):
        source = self.templates / 'resources'
        os.makedirs(destination, 0o700)
        for filepath in source.glob('*'):
            short_name = to_short_name(filepath)
            if short_name not in role_settings[self.mode]['filtered']:
                shutil.copy2(filepath, destination)

        if 'peer' == self.mode:
            return

        self.run_patches(role_settings[self.mode]['patches'])

    def run_patches(self, patch_map):
        for short_name, patch_cb in patch_map.items():
            patch_config(self.dir, short_name, patch_cb)

    def prepare_peers(self):
        num_peers = 20
        destination = self.dir / 'resources'
        for role in ['api', 'p2p']:
            filename = 'peers-{}.json'.format(role)
            select_random_peers(self.templates / 'all-{}'.format(filename), destination / filename, num_peers)

    def prepare_startup_files(self):
        pass
