#!/usr/bin/env bash

projectDir=`pwd`

echo ========================================================
echo Copying sources to micropython project
echo ========================================================
cp -rf $projectDir/sources/* ~/micropython/ports/esp8266/modules

echo ========================================================
echo Rebuilding ESP8266 port
echo ========================================================

export PATH=~/esp-open-sdk/xtensa-lx106-elf/bin:$PATH
cd ~/micropython/ports/esp8266
make clean
make

echo ========================================================
echo Copying output files to build and shared directories
echo ========================================================
cp -f build-GENERIC/firmware-combined.bin "$projectDir/binaries/$(date +"%Y%m%d-%H%M%S").bin"
cp -f build-GENERIC/firmware-combined.bin "$projectDir/binaries/last_build.bin"
cp -f build-GENERIC/firmware-combined.bin "/media/sf_shared/outputs/last_build.bin"