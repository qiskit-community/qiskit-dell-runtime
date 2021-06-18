#!/usr/bin/env bash
set -e -x

python3 --version

git config --global user.email "nobody@concourse-ci.org"
git config --global user.name "Concourse"

cd qiskit-runtime-emulator

newVersion=$(cat ci/version | awk -F. -v OFS=. 'NF==1{print ++$NF}; NF>1{if(length($NF+1)>length($NF))$(NF-1)++; $NF=sprintf("%0*d", length($NF), ($NF+1)%(10^length($NF))); print}')
echo $newVersion > ci/version
git add ci/version
git commit -m "[ci skip] bump version"


