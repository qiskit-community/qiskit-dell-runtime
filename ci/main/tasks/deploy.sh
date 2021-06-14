#!/usr/bin/env bash
set -e -x

echo "Do nothing"
mkdir ~/.kube
cp qre-secrets/kube_config.yaml ~/.kube/config

cd qiskit-runtime-emulator/server/deployments
source test.sh
envsubst < ./qre.yaml | kubectl apply -f -