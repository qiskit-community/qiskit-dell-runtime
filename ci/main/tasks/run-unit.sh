#!/usr/bin/env bash
set -e -x

python3 --version

cd qiskit-runtime-emulator
pip3 install . 

python3 -m pytest
