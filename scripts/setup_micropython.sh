#!/usr/bin/env bash

#changes:
# - changed make execution according to official readme

export PATH=~/esp-open-sdk/xtensa-lx106-elf/bin:$PATH
cd ~/
git clone https://github.com/micropython/micropython.git
cd micropython
git submodule update --init
make -C mpy-cross
cd ports/esp8266

make
#make axtls
#make -j12a
