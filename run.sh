#!/bin/bash

set -e

curr_dir=`pwd`
script_dir=$(dirname $(readlink -f "${0}"))
cd ${script_dir}

if [ ! -d .venv ]; then
    echo -e '\033[31mVirtual Environment Not Installed!\033[0m\nRun \033[36m./install.sh\033[0m to install it.\033[0m';
    exit 1;
fi

source .venv/bin/activate
python3.12 main.py

cd ${curr_dir}