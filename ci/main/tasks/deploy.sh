#!/usr/bin/env bash
set -e -x

mkdir ~/.kube
cp qre-secrets/kube_config.yaml ~/.kube/config

cd qiskit-runtime-emulator/server/deployments
source test.sh
cd ..
{
    make clean
} || {

}
make deploy
cd -
kubectl wait --for=condition=Ready pods --all -n $(echo $QRE_NS)