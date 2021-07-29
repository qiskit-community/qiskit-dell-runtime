export QRE_NS=qre

export DOCKER_REPO=<docker repository>
export MYSQL_IMAGE=<mysql image location in repo>

export KUBE_LOCATION=<cluster IP/URL>
export SERVER_URL="http://$QRE_NS.$KUBE_LOCATION"

export SSO_TOKEN_URL=<sso token url>
export SSO_AUTH_URL=<sso auth url>
export SSO_INFO_URL=<sso user info url>

export REQUESTS_CA_BUNDLE=<path to certificates>
export QRE_CERTS_DIR=<path to directory of required certificates (backends, SSO, etc)>
