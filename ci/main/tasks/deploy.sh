#!/usr/bin/env bash
set -e -x

echo "Do nothing"
mkdir ~/.kube
echo $KUBECONFIG_FILE > ~/.kube/config

# cd qiskit-runtime-emulator/server/deployments
# source test.sh
# envsubst < ./qre.yaml | kubectl apply -f -