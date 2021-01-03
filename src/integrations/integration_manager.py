
import requests
from typing import Any

from flask import abort

class MSALRequestor:
    def __init__(self, user, msal_info, im):
        self.user = user
        self.msal_info = msal_info
        self.im = im

    def refresh_access_token(self):
        response = requests.post(
            "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {self.msal_info['access_token']}"
            },
            data={
                'client_id': "42a46086-81ff-4654-8b30-2eb1b4ea551b",
                'scope': ["mail.read"],
                'refresh_token': self.msal_info['refresh_token'],
                'redirect_uri': "http://localhost:5000/subscribe/outlook",
                'grant_type': 'refresh_token',
                'client_secret': 'WYweb1osVN_5rCo-Gb.q_A2~UI50Ey.2X4'
            }
        )
        if response.status_code == 200:
            data = response.json()
            self.msal_info['access_token'] = data['access_token']
            self.im.add_integration(self.user, "msal", self.msal_info)
            return True
        else:
            return False

    def get(self, request):
        response = requests.get(
            request,
            headers={"Authorization": f"Bearer {self.msal_info['access_token']}"},
        )

        # Check for expired token error.
        if response.status_code == 401:

            # If it worked, then retry the response, otherwise throw a fit.
            if not self.refresh_access_token():
                abort(401, "Could not refresh access token, user needs to sign in again.")

            response = requests.get(
                request,
                headers={"Authorization": f"Bearer {self.msal_info['access_token']}"},
            )

        return response

class IntegrationManager:
    """

    This provides methods for handling integrations for a user. It fails with various exceptions
    when things are not met, which the calling code is responsible for handling.

    """

    def __init__(self, cm):
        self.cm = cm

    def add_integration(self: Any, user: str, integration: str, object: str) -> bool:
        # This returns an empty object if no integrations have been added yet.
        existing_integrations = self.cm.get_integrations(user)

        # Add the user.
        existing_integrations['user'] = user

        # Merge new integration.
        existing_integrations[integration] = object

        # Put the object.
        self.cm.put_integrations(user, existing_integrations)

        return existing_integrations

    def get_integration(self: Any, user: str, integration: str) -> dict:

        # Try and get the integrations for this user.
        integrations = self.cm.get_integrations(user)

        # If no integrations at all, raise a Key Error.
        if len(integrations) == 0:
            raise KeyError(f"No integrations found for {user}.")

        if integration not in integrations.keys():
            raise KeyError(f"No entry found for {integration} on {user}.")
        else:
            return integrations[integration]

    def get_requestor(self, user, integration):

        requestor_map = {
            'msal': MSALRequestor
        }

        # Try and get the integrations for this user.
        integrations = self.cm.get_integrations(user)

        # If no integrations at all, raise a Key Error.
        if len(integrations) == 0:
            raise KeyError(f"No integrations found for {user}.")

        if integration not in integrations.keys():
            raise KeyError(f"No entry found for {integration} on {user}.")
        else:
            return MSALRequestor(user, integrations[integration], self)


    def list_integrations(self: Any, user: str) -> list:
        """Return a list of the integrations belonging to the specified user.

        Looks up the integration entries for the user in the database and simply returns
        the list of keys, not the actual integration information itself.

        It does NO checking on whether those integrations are still valid or not.

        Arguments:
            user: A string identifying the id of the user.

        Returns:
            list: A list of strings identifying each integration.

        """
        # Try and get the integrations for this user.
        integrations = self.cm.get_integrations(user)

        # If no integrations at all, raise a Key Error.
        if len(integrations) == 0:
            raise KeyError(f"No integrations found for {user}.")

        return list(integrations.keys())
