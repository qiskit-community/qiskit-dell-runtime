export QDR_NS=qdr

export DOCKER_REPO=dellemctrigr # default - if you make modifications change to your repo! 

# 
export DB_IMAGE=mysql:5.6
export DB_TYPE=mysql
export DB_NAME=mysql
export DB_NAME=${DB_NAME,,}
export DB_UPPER=${DB_NAME^^}
export DB_DATABASE=qdr
export DB_USER=qdr
export DB_PORT=3306

# You may need to modify these if your cluster does not have
# an associated DNS name on your network.
export KUBE_LOCATION=<cluster IP/URL>
export SERVER_URL="http://$QDR_NS.$KUBE_LOCATION"

# Uncomment and modify if you would like to incorporate your own SSO

# export SSO_TOKEN_URL=<token URL>
# export SSO_AUTH_URL=<auth URL>
# export SSO_INFO_URL=<info URL>
# export SSO_SCOPE=<sso scope>
# export SSO_CLIENT_ID=<client id>
# export SSO_CLIENT_SECRET=<client secret


# If you are behind a firewall, you may need to make use of these.

# export REQUESTS_CA_BUNDLE=<certificate path>
# export QDR_CERTS_DIR=<path to certs for pods>