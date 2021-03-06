#!/bin/bash
# Setup scripts for bionetverification scripts

preventSubshell(){
  if [[ $_ != $0 ]]
  then
    :
  else
    echo "Script is a subshell - please run the script by invoking . script.sh command";
    exit 1;
  fi
}

preventSubshell

# Get path to containing folder
fullpath=$( realpath "$0" )
dirpath=$( dirname $fullpath )

##################
# Install MiniSat
echo "###Installing MiniSat.."
# sudo apt-get install minisat
sudo dpkg -i .dependencies/minisat_2.2.1.deb
#minisatpath="$dirpath/.dependencies"

# Unnecessary if all Python dependencies are self contained
# Install pip3
# echo "###Installing pip.."
# sudo apt-get install python3-pip

# Install python distutils
# Ubuntu 20.04:
sudo dpkg -i .dependencies/python3-distutils_3.8.5-1~20.04.1_all.deb
# Ubuntu 18.04:
# sudo dpkg -i .dependencies/python3-distutils_3.6.9-1~18.04_all.deb


# Install python dependencies
echo "###Installing python dependencies.."
pydeppath="$dirpath/.dependencies/pydep"
# Install pip
sudo python3 $pydeppath/pip-20.2.4-py2.py3-none-any.whl/pip install --no-index $pydeppath/pip-20.2.4-py2.py3-none-any.whl
# Install all other python dependencies
sudo pip install --no-index --find-links=$pydeppath setuptools
sudo pip install --no-index --find-links=$pydeppath -r $pydeppath/requirements.txt

# sudo pip3 install -r requirements.txt

# Add NuSMV to PATH variable by adding to .profile
echo "###Adding NuSMV to PATH.."
nusmvpath="$dirpath/NuSMV-2.6.0-Linux/bin/NuSMV"
echo "# Allow running NuSMV from terminal" >>~/.profile
echo "export PATH=\$PATH:$dirpath/NuSMV-2.6.0-Linux/bin" >>~/.profile
source ~/.profile
# Add permission for NuSMV execution
chmod u+x $nusmvpath
