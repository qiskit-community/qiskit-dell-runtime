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
* Docker installation capable of making and pushing images and a repository to wich `mysql`, `qiskit`, `qre-base`, `orchestrator`, and `executor` images can be pushed
* A running Kubernetes cluster and `kubectl` installed and configured to manage that cluster
* Kubernetes Secret Generator installed on the cluster via `helm`. Instructions for installing this chart can be found at: https://github.com/mittwald/kubernetes-secret-generator

To deploy the Dell Qiskit Runtime Server, perform the following steps beginning in the `qiskit-runtime-emulator` directory:
* Edit `./server/deployments/prod.sh`:
  * Replace `<cluster IP/URL>` with the IP Address or DNS name of your running Kubernetes cluster
  * Replace `<docker base>` with the root repository for your docker images
  * Replace `<mysql image>` with the name of the location in your docker repository that contains a working `mysql` image.
* `cd server`
* `source deployments/prod.sh`
* `make && make push`
* `make deploy_no_sso`

At this point the deployment will be created in a new namespace named `qre`. You can view the status of the database and orchestrator pods using `kubectl get pods -n qre`.

When both pods are `Running` the deployment is ready to be used via the `EmulatorProvider`'s remote runtime interface.

If you need to remove your deployment, you can run `make clean` from the `server` directory assuming that the environnment variables set in `server/deployments/prod.sh` are still active in your shell.

## Configuring Custom SSO

The Qiskit Runtime Emulator Server can be run in conjunction with SSO if desired. To do so, you must already have an identity provider available - this project does not provide one. If you do have an identity provider like Google, Facebook, or a company SSO available, you can configure the server to authenticate users with that provider.

To do so, make the following changes to `server/deployments/prod.sh`:
* Replace `<auth url>` with the URL your identity provider offers to users to obtain credentials.
* Replace `<token url>` with hte URL your identity provider offers to users to obtain a token once they have logged in.
* Replace `<info url>` with the URL your identity provider offers to obtain information about a user using a valid token.
* Replace `<client id>` with the client ID provided for your registered application with your identity provider.
* Replace `<client secret>` with the client secret provided for your registered application with your identity provider.
* Replace `<sso scope>` with the appropriate/enabled scopes on your identity provider. We only take a name from the user info response so these can be largely minimal with the current configuration.

Once these variables are set in your script, run the following from the `server` directory:
* `source deployments/prod.sh`
* `make && make push`
* `make deploy_with_sso`

The code on the server that interfaces with the SSO provider has occasionally needed certificates uploaded to the pod to function. Should you run into an SSL error let us know - we have been able to make it work for some providers but not all.

## Configuring Custom Database

If you'd prefer to use a different database in conjunction with the Dell Qiskit Runtime Emulator Server, you may edit `server/deployments/prod.sh` with the necessary parameters. The server has been tested with `PostgreSQL` and `MySQL`; other databases may require further configuration.

Generally, you may follow these steps to configure a custom database in `server/deployments/prod.sh`:
* Update `DB_IMAGE` with the database image you would prefer to use
* Update `DB_TYPE` and `DB_NAME` with the kind of database you are using; worthy of note is that for `PostgreSQL` `DB_TYPE` should contain "postgresql" while `DB_NAME` should contain "postgres"
* Make any other changes to `DB_DATABASE`, `DB_USER`, or `DB_PORT` that are required.

