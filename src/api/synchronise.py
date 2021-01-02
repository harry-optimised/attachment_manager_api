"""Define the Synchronise API Resource."""

from datetime import datetime
import json
import requests
from typing import Any

from flask import Blueprint, abort, request, redirect, jsonify, Response
from flask_cors import cross_origin
from flask_restx import Api, Resource
from marshmallow import INCLUDE, Schema, fields

from src import app_config, cm
from src.auth import get_user_id, requires_auth
from src.api.subscribers.msal import get_sign_in_flow, get_token_from_code

synchronise_blueprint = Blueprint("synchronise", __name__)
api = Api(synchronise_blueprint)

class Outlook(Resource):

    @requires_auth
    @cross_origin()
    def get(self: Any) -> Any:

        # Todo: Create a manual synchronise route that uses the stores tokens to get all the attachments and save.

        # Todo: Refresh the token using the access token if it's out of date.

        synchronise_from_date = datetime.fromisoformat("2020-08-01T08:00")
        # What are the rate limits on MSAL?

        user_id = get_user_id()
        user_info = cm.get_user(user_id)

        all_messages_parsed = False

        get_messages_url = f'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?' \
                           f'$search="hasAttachments:true"' \
                           f'&$select=id,receivedDateTime,sender' \
                           f'&top=100'

        # Todo: I'm assuming the search is ordered by most recent, which may not be a valid assumption.
        # Todo: Manually put a rate limit on it?

        # Todo: We want to filter these attachments somehow, a lot are just noisy rubbish.

        # Todo: This route needs to be launched as a job and return at a later time, with callback maybe?

        while not all_messages_parsed:

            print("Requesting emails.")
            response = requests.get(
                get_messages_url,
                headers={"Authorization": f"Bearer {user_info['msal']['access_token']}"},
            )
            if response.status_code == requests.codes.ok:
                data = response.json()
                emails = data['value']

                # Exit Condition.
                if '@odata.nextLink' in data.keys():
                    get_messages_url = data['@odata.nextLink']
                else:
                    all_messages_parsed = True

                file_data = []
                for e in emails:
                    id = e['id']
                    received_datetime = e['receivedDateTime'].replace("Z", "")
                    sender = e['sender']['emailAddress']['address']

                    # Exit Condition
                    python_received_datetime = datetime.fromisoformat(received_datetime)
                    if python_received_datetime < synchronise_from_date:
                        all_messages_parsed = True
                        break;

                    print(received_datetime)

                    attachment_response = requests.get(
                        f'https://graph.microsoft.com/v1.0/me/messages/{id}/attachments'
                        f'?select=contentType,name,isInline',
                        headers={"Authorization": f"Bearer {user_info['msal']['access_token']}"},
                    )
                    if attachment_response.status_code == requests.codes.ok:

                        attachment_data = attachment_response.json()
                        attachments = attachment_data['value']
                        print(f"Processing {len(attachments)} attachments.")
                        for a in attachments:
                            attachment_type = a['contentType']
                            attachment_name = a['name']
                            inline = a['isInline']

                            if not inline:
                                file_data.append({
                                    'name': attachment_name,
                                    'created': received_datetime,
                                    'sender': sender,
                                    'type': attachment_type
                                })
                    else:
                        abort(response.status_code, f"Unable to get attachment: {response.text}")

            else:
                abort(response.status_code, f"Unable to get emails: {response.text}")

        # Add all files to the database for this user.
        for file in file_data:
            cm.put_file(user_id, file)

        return {'message': f"{len(file_data)} attachments added to the database."}, 200


api.add_resource(Outlook, "/synchronise/outlook")