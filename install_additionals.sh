#!/bin/bash
# Setup scripts for bionetverification scripts

# Update package index
apt-get update

# Install MiniSat
echo '###Installing MiniSat..'
apt-get install minisat

# Install pip3
echo '###Installing pip..'
apt-get install python3-pip

# Install python dependencies
echo '###Installing python dependencies..'
pip3 install -r requirements.txt

# Add NuSMV to PATH variable by adding to .profile
echo '# Allow running NuSMV from terminal' >>~/.profile
echo 'export PATH=$PATH:$PWD/NuSMV-2.6.0-Linux/bin' >>~/.profile