#!/bin/bash
# Setup scripts for bionetverification scripts

preventSubshell(){
  if [[ $_ != $0 ]]
  then
    echo "Script is being sourced"
  else
    echo "Script is a subshell - please run the script by invoking . script.sh command";
    exit 1;
  fi
}

# Update package index
sudo apt-get update

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