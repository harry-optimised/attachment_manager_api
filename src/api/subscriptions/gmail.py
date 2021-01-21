"""Define the Subscribe API Resource."""

from typing import Any

from authlib.integrations.requests_client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery
from flask import Blueprint, redirect, request, session
from flask_cors import cross_origin
from flask_restx import Api, Resource

from src.auth import get_user_id
from src.config import app_config
from src.integration_manager import im
from src.integrations.msal import get_sign_in_flow, get_token_from_code

subscribe_blueprint = Blueprint("subscribe", __name__)
api = Api(subscribe_blueprint)


class Gmail(Resource):
    @cross_origin()
    def get(self: Any) -> Any:

        code = request.args.get("code")

        # If this is a request from the front end then start the authorisation flow and
        # respond back with the authentication URL that the FE must redirect to.
        if code is None:

            # This is actually how this route is protected, this line will fail with
            # an auth error if no authentication is provided, whilst leaving the rest of
            # the subscription open for microsoft to respond to.
            id = get_user_id()

            flow = OAuth2Session(
                app_config['GOOGLE_APP_ID'],
                app_config['GOOGLE_APP_SECRET'],
                scope=app_config['GOOGLE_SCOPES'],
                redirect_uri=app_config['GOOGLE_REDIRECT']
            )

            uri, state = flow.create_authorization_url(app_config['GOOGLE_AUTHORITY'])

            session["flow"] = {"state": state, "user": id}

            return {"auth_endpoint": uri}, 200


        # Otherwise, it's a response from Microsoft, so process the response, combine it
        # with the saved flow and complete the authentication.
        else:

            state = session["flow"]["state"]
            user = session["flow"]["user"]

            req_state = request.args.get('state', default=None, type=None)
            if req_state != state:
                abort(401, "Invalid state parameter.")

            flow = OAuth2Session(
                app_config['GOOGLE_APP_ID'],
                app_config['GOOGLE_APP_SECRET'],
                state=state,
                redirect_uri=app_config['GOOGLE_REDIRECT']
            )

            integration_object = flow.fetch_token(
                'https://www.googleapis.com/oauth2/v4/token',
                authorization_response=request.url)

            im.add_integration(user, "google", integration_object)

            return redirect("http://localhost:3000/")

