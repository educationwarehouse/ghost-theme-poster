#!/usr/bin/env python3
import shutil, pathlib, os, datetime, sys
from invoke import task 
import httpx 
import jwt 
import json 
import yaml 

# 'admin_api_key': 'Admin API key from a new integration from the integrations page.' 
@task(
  help={
    'site':'domein, tevens folder naam', 
  }
)
def push(ctx, site):
  "Pakt {site}/ in als {site}.zip en verstuur naar ghost. "
  with open('.ghost-keys','r') as secrets:
    try:
      admin_api_key = yaml.load(secrets.read(),yaml.Loader)[site]
    except KeyError:
      print(f'{site} komt niet voor in .ghost-keys yaml config file. ',file=sys.stderr)
      exit(255)
  archive = pathlib.Path(f"{site}.zip")
  shutil.make_archive(str(archive).replace('.zip',''), "zip", site)  
  # api versioning: https://ghost.org/docs/faq/api-versioning/ 
  url = f'https://{site}/ghost/api/v3/admin/themes/upload'
  #token = token if token else os.getenv(f"{site.upper()}_GHOST_TOKEN")
  # curl -X POST -F 'file=@/path/to/themes/my-theme.zip' -H "Authorization: Ghost $token" https://{admin_domain}/ghost/api/{version}/admin/themes/upload  
 
  # https://ghost.org/docs/admin-api/#token-authentication
 
  id, secret = admin_api_key.split(':')
  # Prepare header and payload
  iat = int(datetime.datetime.now().timestamp())
  header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
  payload = {
    'iat': iat,
    'exp': iat + 5 * 60,
    'aud': '/v3/admin/'
  }
  # Create the token (including decoding secret)
  token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)
  
  
  resp = httpx.post(
    url,
    headers={'Authorization':f'Ghost {token}'},
    files={'file':archive.open('rb')}, 
    verify=False
  )
  print(json.dumps(resp.json(), indent=2))
