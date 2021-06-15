#!/usr/bin/env bash
set -e -x

mkdir ~/.kube
cp qre-secrets/kube_config.yaml ~/.kube/config

cd qiskit-runtime-emulator/server/deployments
source test.sh
{
    envsubst < ./qre.yaml | kubectl delete -f - &&
} || {

}
envsubst < ./qre.yaml | kubectl apply -f -

kubectl wait --for=condition=Ready pods --all -n $(echo $QRE_NS)