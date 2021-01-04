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
    def __init__(self: Any, user: str, msal_info: dict, im: Any) -> None:
        self.user = user
        self.msal_info = msal_info
        self.im = im

    def refresh_access_token(self: Any) -> bool:
        response = requests.post(
            "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {self.msal_info['access_token']}",
            },
            data={
                "client_id": "42a46086-81ff-4654-8b30-2eb1b4ea551b",
                "scope": ["mail.read"],
                "refresh_token": self.msal_info["refresh_token"],
                "redirect_uri": "http://localhost:5000/subscribe/outlook",
                "grant_type": "refresh_token",
                "client_secret": "WYweb1osVN_5rCo-Gb.q_A2~UI50Ey.2X4",
            },
        )
        if response.status_code == 200:
            data = response.json()
            self.msal_info["access_token"] = data["access_token"]
            self.im.add_integration(self.user, "msal", self.msal_info)
            return True
        else:
            return False

    def get(self: Any, request: Any) -> Any:
        response = requests.get(
            request,
            headers={"Authorization": f"Bearer {self.msal_info['access_token']}"},
        )

        # Check for expired token error.
        if response.status_code == 401:

            # If it worked, then retry the response, otherwise throw a fit.
            if not self.refresh_access_token():
                abort(
                    401, "Could not refresh access token, user needs to sign in again."
                )

            response = requests.get(
                request,
                headers={"Authorization": f"Bearer {self.msal_info['access_token']}"},
            )

        return response
