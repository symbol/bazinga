#!/usr/bin/env python3

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from subprocess import PIPE, STDOUT, Popen

from symbolchain.core.CryptoTypes import PrivateKey
from symbolchain.core.PrivateKeyStorage import PrivateKeyStorage
from symbolchain.core.sym.KeyPair import KeyPair
from zenlog import log


def run_openssl(args, show_output=True):
    command_line = ['openssl'] + args
    process = Popen(command_line, stdout=PIPE, stderr=STDOUT)

    all_lines = []
    for line_bin in iter(process.stdout.readline, b''):
        line = line_bin.decode('ascii')
        all_lines.append(line)

        if show_output:
            sys.stdout.write(line)
            sys.stdout.flush()

    process.wait()

    return all_lines


def check_openssl_version():
    version_output = ''.join(run_openssl(['version', '-v'], False))
    match = re.match(r'^OpenSSL +([^ ]*) ', version_output)
    if not match or not match.group(1).startswith('1.1.1'):
        raise RuntimeError('{} requires openssl version >=1.1.1'.format(__file__))


def get_common_name(default_value, prompt):
    if default_value:
        return default_value

    return input('Enter {}: '.format(prompt)).strip()


def prepare_ca_config(ca_pem_path, ca_cn):
    with open('ca.cnf', 'wt') as output_file:
        output_file.write('''[ca]
default_ca = CA_default

[CA_default]
new_certs_dir = ./new_certs

database = index.txt
serial   = serial.dat
private_key = {private_key_path}
certificate = ca.crt.pem
policy = policy_catapult

[policy_catapult]
commonName              = supplied

[req]
prompt = no
distinguished_name = dn

[dn]
CN = {cn}
'''.format(private_key_path=ca_pem_path, cn=ca_cn))

    os.makedirs('new_certs')
    os.chmod('new_certs', 0o700)

    with open('index.txt', 'wt') as output_file:
        output_file.write('')


def prepare_node_config(node_cn):
    with open('node.cnf', 'wt') as output_file:
        output_file.write('''[req]
prompt = no
distinguished_name = dn
[dn]
CN = {cn}
'''.format(cn=node_cn))


def main():
    parser = argparse.ArgumentParser(description='Cert generation tool', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--output', help='certificates working directory (all files will be created inside)', default='certificates')
    parser.add_argument('--ca', help='path to key PEM file that will be used as a CA key', default='ca.key.pem')
    parser.add_argument('--name-ca', help='use provided name as CA CN (common name) - suggested: account name')
    parser.add_argument('--name-node', help='use provided name as node CN (common name) - suggested: node name, host or ip')
    parser.add_argument('--force', help='overwrite output directory if it already exists', action='store_true')
    args = parser.parse_args()

    filepath = Path(args.output)
    if filepath.exists():
        if not args.force:
            raise FileExistsError('output directory ({}) already exists, use --force to overwrite'.format(filepath))
        shutil.rmtree(filepath)

    check_openssl_version()

    # obtain full path prior to switching directory
    ca_path = Path(args.ca).absolute()

    os.makedirs(filepath)
    os.chdir(filepath)

    log.info('creating ca.pubkey.pem')
    run_openssl(['pkey', '-in', ca_path, '-pubout', '-out', 'ca.pubkey.pem'])

    log.info('creating random node.key.pem')
    node_key_pair = KeyPair(PrivateKey.random())
    PrivateKeyStorage('.', None).save('node.key', node_key_pair.private_key)

    log.info('preparing configuration files')
    ca_cn = get_common_name(args.name_ca, 'CA common name')
    node_cn = get_common_name(args.name_node, 'node common name')
    prepare_ca_config(ca_path, ca_cn)
    prepare_node_config(node_cn)

    log.info('creating CA certificate')
    run_openssl([
        'req',
        '-config', 'ca.cnf',
        '-keyform', 'PEM',
        '-key', ca_path,
        '-new', '-x509',
        '-days', '7300',
        '-out', 'ca.crt.pem'])

    # prepare node CSR
    run_openssl([
        'req',
        '-config', 'node.cnf',
        '-key', 'node.key.pem',
        '-new',
        '-out', 'node.csr.pem'])

    log.info('signing node certificate')
    run_openssl(['rand', '-out', './serial.dat', '-hex', '19'])

    run_openssl([
        'ca',
        '-config', 'ca.cnf',
        '-days', '375',
        '-notext',
        '-batch',
        '-in', 'node.csr.pem',
        '-out', 'node.crt.pem'])

    log.info('certificates generated in {} directory'.format(args.output))


if __name__ == '__main__':
    main()
