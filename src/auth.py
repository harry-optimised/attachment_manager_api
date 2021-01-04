"""Define functions, decorators, and errors for dealing with authentication."""

import json
from functools import wraps
from typing import Any

import requests
from flask import _request_ctx_stack, abort, request
from jose import jwt
from six.moves.urllib.request import urlopen

from src.config import app_config


def get_token_auth_header() -> str:
    """Obtain the Access Token from the Authorization Header."""
    auth = request.headers.get("Authorization", None)
    if not auth:
        abort(401, "Authorization header was missing.")

    parts = auth.split()

    if parts[0].lower() != "bearer":
        abort(401, "Authorization header must start with:  'Bearer'")
    elif len(parts) == 1:
        abort(401, "JWT Token not found. Are you authenticated?")
    elif len(parts) > 2:
        abort(401, "Authorization header be a 'Bearer' token.")

    return parts[1]


def authenticate_token(token: str) -> bool:
    """Authenticate the provided JWT token using Auth0."""
    jsonurl = urlopen(f"{app_config['AUTH_TENANT_URL']}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=app_config["AUTH_JWT_AUDIENCE"],
                issuer=f"{app_config['AUTH_TENANT_URL']}/",
            )
        except jwt.ExpiredSignatureError:
            abort(401, "Token has expired.")
        except jwt.JWTClaimsError:
            abort(401, "Incorrect claims, please check the audience and issuer.")
        except Exception:
            abort(401, "Unable to parse authentication token.")

        _request_ctx_stack.top.current_user = payload
        return True
    abort(401, "Unable to find RSA key.")


def requires_auth(f: Any) -> Any:
    """Decorate a function by validating the Access Token."""

    @wraps(f)
    def decorated(*args: list, **kwargs: dict) -> Any:
        token = get_token_auth_header()
        if authenticate_token(token):
            return f(*args, **kwargs)

    return decorated


def get_user_id() -> str:
    """Use the access token to retrieve the user profile and return the email as the user id."""
    token = get_token_auth_header()

    # Try and get user profile data.
    response = requests.get(
        f"{app_config['AUTH_TENANT_URL']}/userinfo",
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code == requests.codes.ok:
        profile_data = response.json()
    else:
        abort(response.status_code, f"Unable to fetch user profile: {response.text}")

    # Extract and return user email.
    if "email" in profile_data.keys():
        return profile_data["email"]
    else:
        abort(
            403,
            "The server was enable to fetch the user email with the provided access token. "
            "Ensure the access token has email scope.",
        )
