# Installation Instructions for Dell Qiskit Runtime Emulator

## Requirements

The following installation guide presumes that the user has at least the following installed:

* Python version 3.7+
* Pip3

## Client Quick Start Guide

The client (and local exxecution) features of the Dell QRE can be installed and used quickly. The steps to install the package are:

* Download the Dell Qiskit Runtime Emulator directory
* From inside the top-level directory, run:
  * `pip3 install .`

At this point, the `qiskit_emulator` package will have been installed on the machine and can be used in Python programs.

## Server Quick Start Guide

The server deployment of the Dell Qiskit Runtime Emulator requirements are:
* Docker installation and a repository for `qiskit`, `qre-base`, `orchestrator`, and `executor` images
* A running Kubernetes cluster and `kubectl` installed and configured to manage that cluster
* Kubernetes Secret Generator installed on the cluster via `helm`. Instructions for installing this chart can be found at: https://github.com/mittwald/kubernetes-secret-generator

To deploy the Dell Qiskit Runtime Server, perform the following steps beginning in the `qiskit-runtime-emulator` directory:
* Edit `./server/deployments/prod.sh`:
  * Replace `<cluster IP/URL>` with the IP Address or DNS name of your running Kubernetes cluster
  * Replace `<docker base>` with the root repository for your docker images
  * 
* `cd server`
* `source deployments/prod.sh`
* `make && make push`

## Configuring Custom SSO

## Configuring Custom Database

