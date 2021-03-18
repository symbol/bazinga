# note: default settings assume: peer, non-voting, non-harvesting

HARVESTING_KEY_FILENAME = 'private.harvesting.txt'
VRF_KEY_FILENAME = 'private.vrf.txt'


def read_key(filename):
    return open(filename).read().strip()


# region mode-dependent patching

def patch_api_recovery_extensions(config):
    config['extensions']['extension.addressextraction'] = 'true'
    config['extensions']['extension.mongo'] = 'true'
    config['extensions']['extension.zeromq'] = 'true'


def patch_api_server_extensions(config):
    config['extensions']['extension.filespooling'] = 'true'
    config['extensions']['extension.partialtransaction'] = 'true'
    config['extensions']['extension.harvesting'] = 'false'
    config['extensions']['extension.syncsource'] = 'false'


def patch_api_node_common(config):
    config['node']['enableAutoSyncCleanup'] = 'false'
    config['node']['trustedHosts'] = '127.0.0.1, 172.20.0.25'
    config['node']['localNetworks'] = '127.0.0.1, 172.20.0.25'


def patch_api_node(config):
    patch_api_node_common(config)
    config['localnode']['roles'] = 'Api'


def patch_dual_server_extensions(config):
    config['extensions']['extension.filespooling'] = 'true'
    config['extensions']['extension.partialtransaction'] = 'true'


def patch_dual_node(config):
    patch_api_node_common(config)
    config['localnode']['roles'] = 'Peer,Api'

# endregion


# region feature dependent patching

def patch_harvesting(config):
    harvesting_private_key = read_key(HARVESTING_KEY_FILENAME)
    vrf_private_key = read_key(VRF_KEY_FILENAME)

    config['harvesting']['enableAutoHarvesting'] = 'true'
    config['harvesting']['harvesterSigningPrivateKey'] = harvesting_private_key
    config['harvesting']['harvesterVrfPrivateKey'] = vrf_private_key


def patch_voting(config):
    config['finalization']['enableVoting'] = 'true'
    config['finalization']['unfinalizedBlocksDuration'] = '0m'


def patch_voting_node(config):
    config['localnode']['roles'] += ',Voting'

# endregion


role_settings = {
    'peer': {
        'filtered': ['database', 'pt', 'extensions-broker', 'logging-broker', 'messaging']
    },
    'api': {
        'filtered': ['harvesting'],
        'patches': {
            'extensions-server':  patch_api_server_extensions,
            'extensions-recovery': patch_api_recovery_extensions,
            'node':  patch_api_node,
        }
    },
    'dual': {
        'filtered': [],
        'patches': {
            'extensions-server': patch_dual_server_extensions,
            'extensions-recovery': patch_api_recovery_extensions,
            'node':  patch_dual_node,
        }
    }
}
node_settings = {
    'harvesting': {
        'harvesting': patch_harvesting
    },
    'voting': {
        'finalization': patch_voting,
        'node': patch_voting_node
    }
}
