#!/usr/bin/env bash
set -e -x

python3 --version

cd qiskit-runtime-emulator
pip3 install . 

pytest acceptance_tests/
