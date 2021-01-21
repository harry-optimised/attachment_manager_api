from typing import Any

import msal
import requests
from flask import abort

class GoogleRequestor:
    def __init__(self: Any, user: str, google_info: dict, im: Any, app_config: dict) -> None:
        self.user = user
        self.google_info = google_info
        self.im = im
        self.app_config = app_config

    def refresh_access_token(self: Any) -> bool:
        response = requests.post(
            f"{self.app_config['MSAL_AUTHORITY']}/oauth2/v2.0/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {self.google_info['access_token']}",
            },
            data={
                "client_id": self.app_config['MSAL_APP_ID'],
                "scope": self.app_config['MSAL_SCOPES'],
                "refresh_token": self.google_info["refresh_token"],
                "redirect_uri": self.app_config['MSAL_REDIRECT'],
                "grant_type": "refresh_token",
                "client_secret": self.app_config['MSAL_APP_SECRET'],
            },
        )
        if response.status_code == 200:
            data = response.json()
            self.google_info["access_token"] = data["access_token"]
            self.im.add_integration(self.user, "msal", self.google_info)
            return
        else:
            abort(
                401, f"Could not refresh access token: {response.text}"
            )

    def get(self: Any, request: Any) -> Any:
        response = requests.get(
            request,
            headers={"Authorization": f"Bearer {self.google_info['access_token']}"},
        )

        # Check for expired token error.
        if response.status_code == 401:

            # Try and refresh the access token.
            #self.refresh_access_token()

            response = requests.get(
                request,
                headers={"Authorization": f"Bearer {self.google_info['access_token']}"},
            )

        return response
