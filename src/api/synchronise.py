"""Define the Synchronise API Resource."""

from datetime import datetime
import json
import requests
from typing import Any

from flask import Blueprint, abort, request, redirect, jsonify, Response
from flask_cors import cross_origin
from flask_restx import Api, Resource
from marshmallow import INCLUDE, Schema, fields

from src import app_config, cm, im
from src.auth import get_user_id, requires_auth

synchronise_blueprint = Blueprint("synchronise", __name__)
api = Api(synchronise_blueprint)

class Outlook(Resource):

    def _attachment_generator(self: Any, email, msal_requestor):

        attachment_response = msal_requestor.get(
            f'https://graph.microsoft.com/v1.0/me/messages/{email["id"]}/attachments'
            f'?select=contentType,name,isInline'
        )

        if attachment_response.status_code == requests.codes.ok:
            attachment_data = attachment_response.json()
            for a in attachment_data['value']:
                if not a['isInline']:
                    yield {
                        'name': a['name'],
                        'created': email['receivedDateTime'],
                        'sender': email['sender']['emailAddress']['address'],
                        'type': a['contentType']
                    }
        else:
            abort(response.status_code, f"Unable to get attachment: {response.text}")


    def _email_generator(self, from_datetime, msal_requestor):

        get_messages_url = f'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?' \
                           f'$search="hasAttachments:true"' \
                           f'&$select=id,receivedDateTime,sender' \
                           f'&top=100'

        # Define a closure that tests for emails beyond the date range.
        def out_of_date_range(received_datetime):
            return datetime.fromisoformat(received_datetime) < from_datetime

        while True:

            response = msal_requestor.get(get_messages_url)

            if response.status_code != requests.codes.ok:
                abort(response.status_code, f"Unable to get emails: {response.text}")
            else:
                data = response.json()
                emails = data['value']

                # Exit Condition.
                if '@odata.nextLink' in data.keys():
                    get_messages_url = data['@odata.nextLink']
                else:
                    return

                for email in emails:
                    email['receivedDateTime'] = email['receivedDateTime'].replace("Z", "")

                    # Exit if email beyond date range.
                    if out_of_date_range(email['receivedDateTime']):
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
            msal_requestor = im.get_requestor(id, integration='msal')
        except KeyError:
            abort(406, "No MSAL integration found for this user, have you subscribed yet?")

        # Iterate through all valid emails and process the attachments.
        file_data = []
        email_generator = self._email_generator(from_datetime, msal_requestor)
        for email in email_generator:
            attachment_generator = self._attachment_generator(email=email, msal_requestor=msal_requestor)
            for attachment in attachment_generator:
                file_data.append(attachment)

        # Add all files to the database for this user.
        for file in file_data:
            cm.put_file(id, file)

        return {'message': f"{len(file_data)} attachments added to the database."}, 200

api.add_resource(Outlook, "/synchronise/outlook")