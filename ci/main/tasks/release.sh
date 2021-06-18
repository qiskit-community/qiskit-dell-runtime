#!/usr/bin/env bash
set -e -x

python3 --version

git config --global user.email "nobody@concourse-ci.org"
git config --global user.name "Concourse"

cd qre-secrets

newVersion=$(cat version | awk -F. -v OFS=. 'NF==1{print ++$NF}; NF>1{if(length($NF+1)>length($NF))$(NF-1)++; $NF=sprintf("%0*d", length($NF), ($NF+1)%(10^length($NF))); print}')
echo $newVersion > version

git add version
git commit -m "[ci skip] bump version"

cd ../qiskit-runtime-emulator
git tag -a $newVersion -m "CICD Build Tag"

# cd ..
# cp -r qiskit-runtime-emulator/ ibm-repo/

# cd ibm-repo
# git add . 
# git commit -m "build $newVersion"
# git tag -a $newVersion -m "CICD Build Tag"


