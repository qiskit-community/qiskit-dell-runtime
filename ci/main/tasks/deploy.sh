#!/usr/bin/env bash
set -e -x

mkdir -p ~/.kube
cp qre-secrets/kube_config.yaml ~/.kube/config

cd qiskit-runtime-emulator/server/deployments
source test.sh
cd ..
{
    make clean
} || {
    echo "failure in clean"
}
make deploy
cd -
kubectl wait --for=condition=Ready pods --timeout=60s --all -n $(echo $QRE_NS)