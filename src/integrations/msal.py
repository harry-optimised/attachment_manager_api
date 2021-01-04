from typing import Any

import msal
import requests
from flask import abort


def get_msal_app(app_config: dict, cache: Any = None) -> Any:
    # Initialize the MSAL confidential client
    auth_app = msal.ConfidentialClientApplication(
        app_config["MSAL_APP_ID"],
        authority=app_config["MSAL_AUTHORITY"],
        client_credential=app_config["MSAL_APP_SECRET"],
        token_cache=None,
    )

    return auth_app


def get_sign_in_flow(app_config: dict) -> dict:
    auth_app = get_msal_app(app_config)

    return auth_app.initiate_auth_code_flow(
        app_config["MSAL_SCOPES"], redirect_uri=app_config["MSAL_REDIRECT"]
    )


def get_token_from_code(app_config: dict, request: Any, flow: dict) -> dict:
    cache = msal.SerializableTokenCache()
    auth_app = get_msal_app(app_config, cache)
    result = auth_app.acquire_token_by_auth_code_flow(flow, dict(request.args))
    return result


class MSALRequestor:
    def __init__(self: Any, user: str, msal_info: dict, im: Any, app_config: dict) -> None:
        self.user = user
        self.msal_info = msal_info
        self.im = im
        self.app_config = app_config

    def refresh_access_token(self: Any) -> bool:
        response = requests.post(
            f"{self.app_config['MSAL_AUTHORITY']}/oauth2/v2.0/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {self.msal_info['access_token']}",
            },
            data={
                "client_id": self.app_config['MSAL_APP_ID'],
                "scope": self.app_config['MSAL_SCOPES'],
                "refresh_token": self.msal_info["refresh_token"],
                "redirect_uri": self.app_config['MSAL_REDIRECT'],
                "grant_type": "refresh_token",
                "client_secret": self.app_config['MSAL_APP_SECRET'],
            },
        )
        if response.status_code == 200:
            data = response.json()
            self.msal_info["access_token"] = data["access_token"]
            self.im.add_integration(self.user, "msal", self.msal_info)
            return
        else:
            abort(
                401, f"Could not refresh access token: {response.text}"
            )

    def get(self: Any, request: Any) -> Any:
        response = requests.get(
            request,
            headers={"Authorization": f"Bearer {self.msal_info['access_token']}"},
        )

        # Check for expired token error.
        if response.status_code == 401:

            # Try and refresh the access token.
            self.refresh_access_token()

            response = requests.get(
                request,
                headers={"Authorization": f"Bearer {self.msal_info['access_token']}"},
            )

        return response
