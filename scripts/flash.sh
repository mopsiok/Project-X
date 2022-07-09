#!/usr/bin/env bash

comport=$1

echo ========================================================
echo Flashing device via $comport
echo ========================================================

python3 -m esptool --port $comport erase_flash
sleep 2
python3 -m esptool --port $comport --baud 115200 write_flash --flash_size=detect 0 binaries/last_build.bin