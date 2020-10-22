#!/bin/bash
# Setup scripts for bionetverification scripts

# Update package index
apt-get update

# Install MiniSat
echo "###Installing MiniSat.."
sudo apt-get install minisat

# Install pip3
echo "###Installing pip.."
sudo apt-get install python3-pip

# Install python dependencies
echo "###Installing python dependencies.."
sudo pip3 install -r requirements.txt

# Add NuSMV to PATH variable by adding to .profile
echo "###Adding NuSMV to PATH.."
fullpath=$( realpath "$0" )
dirpath=$( dirname $fullpath )
echo "# Allow running NuSMV from terminal" >>~/.profile
echo "export PATH=\$PATH:$dirpath/NuSMV-2.6.0-Linux/bin" >>~/.profile
source ~/.profile