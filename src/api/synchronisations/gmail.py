"""Define the Gmail Synchronise API Resource."""

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


class Gmail(Resource):

    def _attachment_generator(self: Any, email: dict, google_requestor: Any) -> Any:

        # Nice examples of getting attachment data.
        # https://stackoverflow.com/questions/25832631/download-attachments-from-gmail-using-gmail-api

        # Make the request using the requestor object (which handles reauthenticating if required).
        response = google_requestor.get(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{email['id']}"
        )

        if response.status_code == requests.codes.ok:
            data = response.json()

            # Get meta info.
            sender = ""
            received = ""

            for header in data['payload']['headers']:
                if header['name'] == 'From':
                    sender = header['value'].split('>')[0].split('<')[1]
                if header['name'] == 'Date':
                    dt = ' '.join(header['value'].split(' ')[:5])
                    dt = datetime.strptime(dt, '%a, %d %b %Y %H:%M:%S')
                    received = dt.isoformat()

            for part in data['payload']['parts']:
                if part['filename']:
                    yield {
                        "name": part['filename'],
                        "created": received,
                        "sender": sender,
                        "type": part['mimeType'],
                        "link": f"https://mail.google.com/mail/#inbox/{email['id']}",
                    }
        else:
            abort(response.status_code, f"Unable to get attachment: {response.text}")

    def _email_generator(self: Any, from_datetime: str, google_requestor: Any) -> Any:

        get_messages_url = (
            "https://gmail.googleapis.com/gmail/v1/users/me/messages?"
            'q="has:attachment after:2021/01/01"'
            '&maxResults=100'
        )

        while True:

            # Make the request using the requestor object (which handles reauthenticating if required).
            response = google_requestor.get(get_messages_url)

            # Assuming the request succeeded, iterate through the emails, returning each one in turn.
            # This automatically handles exiting when the email are beyond the date limit or no more emails.
            if response.status_code != requests.codes.ok:
                abort(response.status_code, f"Unable to get emails: {response.text}")
            else:
                data = response.json()
                emails = data["messages"]

                for email in emails:
                    yield email

                # Exit Condition.
                if "nextPageToken" in data.keys():
                    get_messages_url = (
                        "https://gmail.googleapis.com/gmail/v1/users/me/messages?"
                        'q="has:attachment after:2021/01/01"'
                        '&maxResults=100'
                        f'&pageToken={data["nextPageToken"]}'
                    )
                else:                    
                    return

    @requires_auth
    @cross_origin()
    def get(self: Any) -> Any:

        print("Starting Processing.")

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
            google_requestor = im.get_requestor(id, integration="google")
        except KeyError:
            abort(
                406, "No Google integration found for this user, have you subscribed yet?"
            )

        # Iterate through all valid emails and process the attachments.
        file_data = []
        email_generator = self._email_generator(from_datetime, google_requestor)
        for email in email_generator:
            print("Processing Email...")
            attachment_generator = self._attachment_generator(
                email=email, google_requestor=google_requestor
            )
            for attachment in attachment_generator:
                file_data.append(attachment)

        # Add all files to the database for this user.
        for file in file_data:
            cm.put_file(id, file)

        return {"message": f"{len(file_data)} attachments added to the database."}, 200