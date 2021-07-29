export QRE_NS=qre-test-ps

export DOCKER_REPO=harbor.dell.com/dojo-harbor

export DB_IMAGE=postgres:latest
export DB_TYPE=postgresql
export DB_NAME=postgres
export DB_NAME=${DB_NAME,,}
export DB_UPPER=${DB_NAME^^}
export DB_DATABASE=qre
export DB_USER=qre
export DB_PORT=5432

# export DB_IMAGE=qre/mysql:5.6
# export DB_TYPE=mysql
# export DB_NAME=mysql
# export DB_NAME=${DB_NAME,,}
# export DB_UPPER=${DB_NAME^^}
# export DB_DATABASE=qre
# export DB_USER=qre
# export DB_PORT=3306


export KUBE_LOCATION=oro-sandbox-small1.k8s.cec.lab.emc.com
export SERVER_URL="http://$QRE_NS.$KUBE_LOCATION"

export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export QRE_CERTS_DIR=/home/geoff/workspace/qre-secrets
