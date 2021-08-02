export QRE_NS=qre-test

export DOCKER_REPO=harbor.dell.com/dojo-harbor

export DB_IMAGE=qre/mysql:5.6
export DB_TYPE=mysql
export DB_NAME=mysql
export DB_NAME=${DB_NAME,,}
export DB_UPPER=${DB_NAME^^}
export DB_DATABASE=qre
export DB_USER=qre
export DB_PORT=3306

export KUBE_LOCATION=oro-sandbox-small1.k8s.cec.lab.emc.com
export SERVER_URL="http://$QRE_NS.$KUBE_LOCATION"

export SSO_TOKEN_URL="https://appsso.login.scfd.isus.emc.com/oauth/token"
export SSO_AUTH_URL="https://appsso.login.scfd.isus.emc.com/oauth/authorize"
export SSO_INFO_URL="https://appsso.login.scfd.isus.emc.com/userinfo"
export SSO_CLIENT_ID=5c731039-4384-4ea1-b134-c9c9c8e25131
export SSO_CLIENT_SECRET=4d872bf7-5122-4a5d-8d09-3e6f2c7e9139
export SSO_SCOPE="openid, roles, user_attributes"

export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export QRE_CERTS_DIR=/home/geoff/workspace/qre-secrets
