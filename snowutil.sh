#!/bin/bash

# Directory containing this script is used as the Python path
MYDIR=$(dirname $0)
export PYTHONPATH=$MYDIR

# run the CLI
python -m snowboard.cli $*
