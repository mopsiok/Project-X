#!/usr/bin/env bash

export PATH=/home/mopsiok/esp-open-sdk/xtensa-lx106-elf/bin:$PATH
cd ~/micropython/ports/esp8266
make clean
make

cp build-GENERIC/firmware-combined.bin "/media/sf_shared/outputs/$(date +"%Y%m%d-%H%M%S").bin"

read -p "Press enter to exit"
