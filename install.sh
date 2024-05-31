#!/bin/bash

set -e

curr_dir=`pwd`
script_dir=$(dirname $(readlink -f "${0}"))
cd ${script_dir}

rm -rf .venv/
python3.12 -m venv .venv
source .venv/bin/activate
pip3.12 install -r requirements.txt

cd ${curr_dir}