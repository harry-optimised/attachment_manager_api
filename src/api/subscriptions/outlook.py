"""Define the Subscribe API Resource."""

from typing import Any

from flask import Blueprint, redirect, request, session
from flask_cors import cross_origin
from flask_restx import Api, Resource

from src.auth import get_user_id
from src.config import app_config
from src.integration_manager import im
from src.integrations.msal import get_sign_in_flow, get_token_from_code

subscribe_blueprint = Blueprint("subscribe", __name__)
api = Api(subscribe_blueprint)


class Outlook(Resource):
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

            flow = get_sign_in_flow(app_config)
            session["flow"] = {"flow": flow, "user": id}

            return {"auth_endpoint": flow["auth_uri"]}, 200

        # Otherwise, it's a response from Microsoft, so process the response, combine it
        # with the saved flow and complete the authentication.
        else:
            flow = session["flow"]["flow"]
            user = session["flow"]["user"]

            integration_object = get_token_from_code(app_config, request, flow)
            im.add_integration(user, "msal", integration_object)

            return redirect("http://localhost:3000/")
