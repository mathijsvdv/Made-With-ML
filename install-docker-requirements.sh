#!/bin/bash

set -e

# shellcheck disable=SC2139
alias pip="$HOME/anaconda3/bin/pip"

sudo apt-get update \
    && sudo apt-get install -y gcc \
        cmake \
        libgtk2.0-dev \
        libgl1-mesa-dev \
        libgl1-mesa-glx \
        libosmesa6 \
        libosmesa6-dev \
        libglfw3 \
        patchelf \
        unzip \
        unrar \
        zlib1g-dev

pip --no-cache-dir install -U pip pip-tools

# Install requirements
pip --no-cache-dir install -U -r requirements.txt

sudo apt-get clean

sudo rm ./*requirements*.txt
