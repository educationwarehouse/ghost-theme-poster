#!/usr/bin/env python3
import shutil, pathlib, os, datetime, sys
from invoke import task
import httpx
import jwt
import yaml


# 'admin_api_key': 'Admin API key from a new integration from the integrations page.'
@task(
    help={
        "dir": "directory name, the last folder name is usedd as the default domain. PE /home/x/some.domain.com",
        "domain": "which domain to push to, defaults to dir. PE demo.domain.com; if domain is not given production is assumed. ",
        "yes": "Override the prompt thas asks for permission to upload.",
    }
)
def push(ctx, dir, domain=None, yes=False):
    "Packs {site}/ in als {site}.zip en verstuur naar ghost."
    # assume dir is the domain name if no domain is given.
    # this defaults to production only
    to_production = domain is None

    if not domain:
        # take any input, cleanse whitespace, lower it, if empty default to 'n' and test if it's 'yes', or 'y'
        i_am_sure = yes or (
            input("Warning: You are about to upload to production, are you sure? [yN]")
            .strip()
            .lower()
            or "n"
        ) in ("yes", "y")
        if i_am_sure:
            print("Proceding push to production...")
        else:
            print("Either invalid, or the wiser choice...")
            exit(1)
    # dir could be ../project/some.domain.name
    # domain should be some.domain.name unless explicitly defined
    domain = domain or os.path.split(dir)[1]

    # load the api key from the .ghost-keys yaml file
    with open(".ghost-keys", "r") as secrets:
        try:
            admin_api_key = yaml.safe_load(secrets)[domain]
            id, secret = admin_api_key.split(":")
        except KeyError:
            print(
                f"{domain} could not be found in the .ghost-keys yaml config file.",
                file=sys.stderr,
            )
            exit(255)
        # except:
        #     print(
        #         f"{domain}'s entry in .ghost-keys yaml config file is invalid: '{admin_api_key}'. format as 'id:secret'.",
        #         file=sys.stderr,
        #     )
        #     exit(255)

    # pack the files
    archive = pathlib.Path(f"{domain}.zip")
    shutil.make_archive(str(archive).replace(".zip", ""), "zip", dir)

    # api versioning: https://ghost.org/docs/faq/api-versioning/
    url = f"https://{domain}/ghost/api/v3/admin/themes/upload"
    # token = token if token else os.getenv(f"{site.upper()}_GHOST_TOKEN")
    # curl -X POST -F 'file=@/path/to/themes/my-theme.zip' -H "Authorization: Ghost $token" https://{admin_domain}/ghost/api/{version}/admin/themes/upload

    # Prepare header and payload
    # https://ghost.org/docs/admin-api/#token-authentication
    iat = int(datetime.datetime.now().timestamp())
    header = {"alg": "HS256", "typ": "JWT", "kid": id}
    payload = {"iat": iat, "exp": iat + 5 * 60, "aud": "/v3/admin/"}
    # Create the token (including decoding secret)
    token = jwt.encode(
        payload, bytes.fromhex(secret), algorithm="HS256", headers=header
    )

    resp = httpx.post(
        url,
        headers={"Authorization": f"Ghost {token}"},
        files={"file": archive.open("rb")},
        verify=False,
    )
    try:
        print(yaml.dump(resp.json()))
    except:
        print(resp.text)
