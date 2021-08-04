export QRE_NS=qre

export DOCKER_REPO=<docker base>

export DB_IMAGE=<mysql image>
export DB_TYPE=mysql
export DB_NAME=mysql
export DB_NAME=${DB_NAME,,}
export DB_UPPER=${DB_NAME^^}
export DB_DATABASE=qre
export DB_USER=qre
export DB_PORT=3306

export KUBE_LOCATION=<cluster IP/URL>
export SERVER_URL="http://$QRE_NS.$KUBE_LOCATION"

export SSO_TOKEN_URL=<token URL>
export SSO_AUTH_URL=<auth URL>
export SSO_INFO_URL=<info URL>
export SSO_SCOPE=<sso scope>
export SSO_CLIENT_ID=<client id>
export SSO_CLIENT_SECRET=<client secret


export REQUESTS_CA_BUNDLE=<certificate path>
export QRE_CERTS_DIR=<path to certs for pods>