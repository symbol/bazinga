# symbol-node-configurator

[![Build Status](https://travis-ci.com/nemtech/symbol-node-configurator.svg?branch=dev)](https://travis-ci.com/nemtech/symbol-node-configurator)


## Prerequisites:
    python3 -m pip install -r requirements.txt

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
