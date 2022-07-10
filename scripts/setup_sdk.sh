#!/usr/bin/env bash

#changes:
# - added curl
# - changed URL for get-pip for python 2.7
# - fixed GNU bash regexp
# - changed PATH

sudo apt install curl make unrar-free autoconf automake libtool gcc g++ gperf \
  flex bison texinfo gawk ncurses-dev libexpat-dev python-dev python python3-serial \
  sed git unzip bash help2man wget bzip2
sudo apt install python3-dev python3-pip libtool-bin
pip3 install rshell esptool
cd ~/
git clone --recursive https://github.com/pfalcon/esp-open-sdk.git
cd esp-open-sdk
curl https://bootstrap.pypa.io/2.7/get-pip.py --output get-pip.py
sudo python2 get-pip.py
pip2 install pyserial
sed -i 's/GNU bash, version (3\\\.\[1-9\]|4/GNU bash, version (3\\\.\[1-9\]|4|5/' ~/esp-open-sdk/crosstool-NG/configure.ac
make STANDALONE=y