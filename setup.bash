#!/bin/bash

# install all node packages
echo "running 'npm install'"
npm install

# build all used web components
echo "running 'npm run rollup'"
npm run rollup

# create the python virtual environment
echo "running 'python3 -m venv py_venv'"
python3 -m venv py_venv

# allow execution of the activation script in the virtual environment
echo "running 'chmod +x py_venv/bin/activate'"
chmod +x py_venv/bin/activate

# activate the virtual environment
echo "runnning 'source py_venv/bin/activate'"
source py_venv/bin/activate

# install numpy inside the virtual environment
echo "runnning 'python3 -m pip install numpy'"
python3 -m pip install numpy

# deactivate the virtual environment
echo "running 'deactivate'"
deactivate

# allow execution of the python starter script
echo "running 'chmod +x python/starter.bash'"
chmod +x python/starter.bash