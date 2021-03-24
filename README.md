# symbol-node-configurator

[![Build Status](https://travis-ci.com/nemtech/symbol-node-configurator.svg?branch=dev)](https://travis-ci.com/nemtech/symbol-node-configurator)

This repository contains two helper tools:
 * votingkey.py - this is alternative voting key file generator
 * generate.py - actual catapult.server configuration generator, that will be described below

## Prerequisites:

    python3 -m pip install -r requirements.txt

Generator tool assumes that in working directory, there is directory called `certificates`
that contains:
 * `ca.pubkey.pem`
 * `ca.crt.pem`
 * `node.full.crt.pem`
 * `node.crt.pem`
 * `node.key.pem`

When running with `--harvesting` switch, generator tool additionally expects:
 * `private.harvesting.txt` and `private.vrf.txt`, containing respectively harvesting private key and vrf private key in hex OR
 * `private.harvesting.pem` and `private.vrf.pem` pem files, containing private keys, if pem files are password protected
  `--ask-pass` switch needs to be present

When running with `--voting` switch, generator tool additionally expects voting key file:
 * `private_key_tree*.dat` - the file will be MOVED to destination directory,

 note: in case of `--voting` if destination directory contains file with given name, the index will be incremented, until "empty" one
 will be found

## Examples:

All examples assume the script is started from PARENT directory


### Create configuration for api node

    python3 symbol-node-configurator/generator.py --mode api --output ../settings

### Create configuration for harvesting peer node

To create a configuration for harvesting node two files are needed, with keys in hex:
 * private.harvesting.txt
 * private.vrf.txt

    echo "C0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FF" > private.harvesting.txt
    echo "B007B007B007B007B007B007B007B007B007B007B007B007B007B007B007B007" > private.vrf.txt
    python3 symbol-node-configurator/generator.py --mode peer --output ../settings

### Create configuration for harvesting and voting peer node

    echo "C0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FF" > private.harvesting.txt
    echo "B007B007B007B007B007B007B007B007B007B007B007B007B007B007B007B007" > private.vrf.txt
    python3 symbol-node-configurator/generator.py --mode peer --output ../settings --voting

### Create configuration for harvesting and voting DUAL node

    echo "C0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FFEC0FF" > private.harvesting.txt
    echo "B007B007B007B007B007B007B007B007B007B007B007B007B007B007B007B007" > private.vrf.txt
    python3 symbol-node-configurator/generator.py --mode dual --output ../settings --voting
