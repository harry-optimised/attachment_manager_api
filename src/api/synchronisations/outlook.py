"""Define the Outlook Synchronise API Resource."""

from datetime import datetime
from typing import Any

import requests
from flask import abort, request
from flask_cors import cross_origin
from flask_restx import Resource

from src.auth import get_user_id, requires_auth
from src.config import app_config
from src.dynamodb.connection_manager import cm
from src.integration_manager import im


class Outlook(Resource):

    # Keep track of how many times we've called the Graph API so that we don't hit our rate limit.
    request_count = 0

    def _attachment_generator(self: Any, email: dict, msal_requestor: Any) -> Any:

        # Make the request using the requestor object (which handles reauthenticating if required).
        # If too many requests are being made, abort.
        if self.request_count > app_config["GRAPH_API_REQUEST_LIMIT"]:
            abort(
                413,
                "Stopped because this request was making too many calls to the Graph API.",
            )
        response = msal_requestor.get(
            f'https://graph.microsoft.com/v1.0/me/messages/{email["id"]}/attachments'
            f"?select=contentType,name,isInline"
        )
        self.request_count += 1

        if response.status_code == requests.codes.ok:
            data = response.json()
            for a in data["value"]:
                if not a["isInline"]:
                    yield {
                        "name": a["name"],
                        "created": email["receivedDateTime"],
                        "sender": email["sender"]["emailAddress"]["address"],
                        "type": a["contentType"],
                    }
        else:
            abort(response.status_code, f"Unable to get attachment: {response.text}")

    def _email_generator(self: Any, from_datetime: str, msal_requestor: Any) -> Any:

        get_messages_url = (
            "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?"
            '$search="hasAttachments:true"'
            "&$select=id,receivedDateTime,sender"
            "&top=100"
        )

        while True:

            # Make the request using the requestor object (which handles reauthenticating if required).
            # If too many requests are being made, abort.
            if self.request_count > app_config["GRAPH_API_REQUEST_LIMIT"]:
                abort(
                    413,
                    "Stopped because this request was making too many calls to the Graph API.",
                )
            response = msal_requestor.get(get_messages_url)
            self.request_count += 1

            # Assuming the request succeeded, iterate through the emails, returning each one in turn.
            # This automatically handles exiting when the email are beyond the date limit or no more emails.
            if response.status_code != requests.codes.ok:
                abort(response.status_code, f"Unable to get emails: {response.text}")
            else:
                data = response.json()
                emails = data["value"]

                # Exit Condition.
                if "@odata.nextLink" in data.keys():
                    get_messages_url = data["@odata.nextLink"]
                else:
                    return

                for email in emails:
                    email["receivedDateTime"] = email["receivedDateTime"].replace(
                        "Z", ""
                    )

                    # Exit if email beyond date range.
                    if (
                        datetime.fromisoformat(email["receivedDateTime"])
                        < from_datetime
                    ):
                        return

                    yield email

    @requires_auth
    @cross_origin()
    def get(self: Any) -> Any:

        # Validate the request.
        from_datetime = request.args.get("from_datetime")
        if from_datetime is None:
            abort(400, "Query parameter 'from_datetime' is required.")

        try:
            from_datetime = datetime.fromisoformat(from_datetime)
        except ValueError as e:
            abort(400, str(e))

        id = get_user_id()

        # Try and get MSAL integration information, this will throw a KeyError if the msal
        # integration doesn't exist, so handle and return gracefully.
        try:
            msal_requestor = im.get_requestor(id, integration="msal")
        except KeyError:
            abort(
                406, "No MSAL integration found for this user, have you subscribed yet?"
            )

        # Start the request count from 0.
        self.request_count = 0

        # Iterate through all valid emails and process the attachments.
        file_data = []
        email_generator = self._email_generator(from_datetime, msal_requestor)
        for email in email_generator:
            attachment_generator = self._attachment_generator(
                email=email, msal_requestor=msal_requestor
            )
            for attachment in attachment_generator:
                file_data.append(attachment)

        # Add all files to the database for this user.
        for file in file_data:
            cm.put_file(id, file)

        return {"message": f"{len(file_data)} attachments added to the database."}, 200
