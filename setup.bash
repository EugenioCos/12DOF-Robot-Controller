#!/bin/bash

# install all node packages
echo "running 'npm install'"
npm install

# build all used web components
echo "running 'npm run rollup'"
npm run rollup

# create the python virtual environment
echo "running 'python3 -m venv python/py_venv'"
python3 -m venv python/py_venv

# allow execution of the activation script in the virtual environment
echo "running 'chmod +x python/py_venv/bin/activate'"
chmod +x python/py_venv/bin/activate

# activate the virtual environment
echo "runnning 'source python/py_venv/bin/activate'"
source python/py_venv/bin/activate

# install numpy inside the virtual environment
echo "runnning 'python3 -m pip install numpy'"
python3 -m pip install numpy

# deactivate the virtual environment
echo "running 'deactivate'"
deactivate