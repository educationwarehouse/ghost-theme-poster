#!/usr/bin/env python3
import shutil, pathlib, os, datetime, sys
from invoke import task
import httpx
import jwt
import yaml

HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKCYAN = "\033[96m"
OKGREEN = "\033[92m"
WARNING = "\033[93m"
FAIL = "\033[91m"
ENDCOLOR = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"


def create_token(domain):
    """
    Create the right JWT token based on the domain and key (supplied in .ghost-keys).
    This token can be used in the request headers as follows:
    Authorization: Ghost {token}
    """
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

    iat = int(datetime.datetime.now().timestamp())
    header = {"alg": "HS256", "typ": "JWT", "kid": id}
    payload = {"iat": iat, "exp": iat + 5 * 60, "aud": "/v3/admin/"}
    # Create the token (including decoding secret)
    token = jwt.encode(
        payload, bytes.fromhex(secret), algorithm="HS256", headers=header
    )
    return token


# 'admin_api_key': 'Admin API key from a new integration from the integrations page.'
@task(
    help={
        "dir": "Directory name, the last folder name is used as the default domain. e.g. /home/x/some.domain.com",
        "domain": "Which domain to push to, defaults to dir. e.g. demo.domain.com; "
        "if domain is not given, production is assumed. ",
        "yes": "Override the prompt that asks for permission to upload.",
    }
)
def push(ctx, dir, domain=None, yes=False):
    """Packs {site}/ as {site}.zip and send to ghost."""
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
            print("Proceeding with push to production...")
        else:
            print("Either invalid, or the wiser choice...")
            exit(1)
    # dir could be ../project/some.domain.name
    # domain should be some.domain.name unless explicitly defined
    domain = domain or os.path.split(dir)[1]
    token = create_token(domain)

    # pack the files
    archive = pathlib.Path(f"{domain}.zip")
    shutil.make_archive(str(archive).replace(".zip", ""), "zip", dir)

    # api versioning: https://ghost.org/docs/faq/api-versioning/
    url = f"https://{domain}/ghost/api/v3/admin/themes/upload"
    # token = token if token else os.getenv(f"{site.upper()}_GHOST_TOKEN")
    # curl -X POST -F 'file=@/path/to/themes/my-theme.zip' -H "Authorization: Ghost $token" https://{admin_domain}/ghost/api/{version}/admin/themes/upload

    # Prepare header and payload
    # https://ghost.org/docs/admin-api/#token-authentication

    resp = httpx.post(
        url,
        headers={"Authorization": f"Ghost {token}"},
        files={"file": archive.open("rb")},
        verify=False,
    )
    try:
        data = resp.json()
        print(yaml.dump(data))

        try:
            theme = data["themes"][0]

            print(
                # text in yellow or green, depending on activeness:
                (OKGREEN if theme["active"] else WARNING)
                + f"Theme '{theme['name']}' on {domain} is {'active' if theme['active'] else 'inactive'}"
                + ENDCOLOR
            )
        except:
            pass
    except:
        print(resp.text)
