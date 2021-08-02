export QRE_NS=qre-dev

export DOCKER_REPO=harbor.dell.com/dojo-harbor

# export DB_IMAGE=postgres:latest
# export DB_TYPE=postgresql
# export DB_NAME=postgres
# export DB_NAME=${DB_NAME,,}
# export DB_UPPER=${DB_NAME^^}
# export DB_DATABASE=qre
# export DB_USER=qre
# export DB_PORT=5432

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

# export SSO_TOKEN_URL="https://oauth2.googleapis.com/token"
# export SSO_AUTH_URL="https://accounts.google.com/o/oauth2/v2/auth"
# export SSO_INFO_URL="https://www.googleapis.com/oauth2/v2/userinfo"
# export SSO_SCOPE="openid, https://www.googleapis.com/auth/userinfo.profile"
# export SSO_CLIENT_ID="607864084504-k6rt70p8j5as27ltedan9jqbsiav3ee0.apps.googleusercontent.com"
# export SSO_CLIENT_SECRET="SRJzqBHEdjr4vPWNino9UHHo"

export SSO_TOKEN_URL="https://appsso.login.scfd.isus.emc.com/oauth/token"
export SSO_AUTH_URL="https://appsso.login.scfd.isus.emc.com/oauth/authorize"
export SSO_INFO_URL="https://appsso.login.scfd.isus.emc.com/userinfo"
export SSO_CLIENT_ID=5c731039-4384-4ea1-b134-c9c9c8e25131
export SSO_CLIENT_SECRET=4d872bf7-5122-4a5d-8d09-3e6f2c7e9139
export SSO_SCOPE="openid, roles, user_attributes"

export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export QRE_CERTS_DIR=/home/geoff/workspace/qre-secrets
