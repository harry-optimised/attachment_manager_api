from typing import Any

from src.integrations.msal import MSALRequestor


class IntegrationManager:
    """This provides methods for handling integrations for a user.

    It fails with various exceptions when things are not met, which the calling code is responsible for handling.

    """

    def initialise(self: Any, cm: Any, app_config: dict) -> None:
        self.cm = cm
        self.app_config = app_config

    def add_integration(self: Any, user: str, integration: str, object: str) -> bool:
        # This returns an empty object if no integrations have been added yet.
        existing_integrations = self.cm.get_integrations(user)

        # Add the user.
        existing_integrations["user"] = user

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

    def get_requestor(self: Any, user: str, integration: str) -> Any:

        requestor_map = {"msal": MSALRequestor}

        # Try and get the integrations for this user.
        integrations = self.cm.get_integrations(user)

        # If no integrations at all, raise a Key Error.
        if len(integrations) == 0:
            raise KeyError(f"No integrations found for {user}.")

        if integration not in integrations.keys():
            raise KeyError(f"No entry found for {integration} on {user}.")
        else:
            return requestor_map[integration](user, integrations[integration], self)

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


im = IntegrationManager()
