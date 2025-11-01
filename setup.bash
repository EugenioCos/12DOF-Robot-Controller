#!/bin/bash

echo "running 'npm install'"
npm install

echo "running 'npm run rollup'"
npm run rollup

echo "running 'python3 -m venv py_venv'"
python3 -m venv py_venv

echo "running 'chmod +x py_venv/bin/activate'"
chmod +x py_venv/bin/activate

echo "runnning 'source py_venv/bin/activate'"
source py_venv/bin/activate

echo "runnning 'python3 -m pip install numpy'"
python3 -m pip install numpy

echo "running 'deactivate'"
deactivate

echo "running 'chmod +x python/starter.bash'"
chmod +x python/starter.bash