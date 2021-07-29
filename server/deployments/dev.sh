export QRE_NS=qre-dev

export DOCKER_REPO=harbor.dell.com/dojo-harbor
export MYSQL_IMAGE=qre/mysql:5.6

export KUBE_LOCATION=oro-sandbox-small1.k8s.cec.lab.emc.com
export SERVER_URL="http://$QRE_NS.$KUBE_LOCATION"

export SSO_TOKEN_URL="https://appsso.login.scfd.isus.emc.com/oauth/token"
export SSO_AUTH_URL="https://appsso.login.scfd.isus.emc.com/oauth/authorize"
export SSO_INFO_URL="https://appsso.login.scfd.isus.emc.com/userinfo"

export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export QRE_CERTS_DIR=/home/geoff/workspace/qre-secrets
