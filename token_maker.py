
from urllib.parse import urljoin  
import json          
import os
import requests 
from requests_oauthlib import OAuth2Session
import webbrowser
import time
url = "http://qre-dev.oro-sandbox-small1.k8s.cec.lab.emc.com/"
scope = ["openid", "roles", "user_attributes"]
client_id = r"5c731039-4384-4ea1-b134-c9c9c8e25131"
client_secret = r"4d872bf7-5122-4a5d-8d09-3e6f2c7e9139"
res = requests.get(url + "/login")
login_info = json.loads(res.text)
redirect_uri = urljoin(url, f"/callback/{login_info['id']}")
global oauth 
oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)


authorization_url, state = oauth.authorization_url(
    login_info["auth_url"]
)
print(f"Opening webpage {authorization_url}\n")

#TODO: figure out whether this can be done CLI

webbrowser.open_new(authorization_url)

urls = {}
while not urls:
    req = requests.get(url + f"/tokeninfo/{login_info['id']}")
    res = (req.status_code, req.reason, req.text)
    if res[0] == 200:
        urls = json.loads(res[2])
    else:
        time.sleep(2)

global access_token
token = oauth.fetch_token(
    urls["token_url"],
    client_secret=client_secret,
    authorization_response=urls["cb_url"],
)

#print(f'dell sso token response: {token}')

access_token = token["access_token"]
token_file = open("token.sh",'w')
token_file.write("export TOKEN=" + access_token)
token_file.close()
