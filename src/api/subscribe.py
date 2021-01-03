"""Define the Subscribe API Resource."""

from typing import Any

from flask import Blueprint, request, redirect, session, jsonify, Response
from flask_cors import cross_origin
from flask_restx import Api, Resource

from src import cm, im
from src.auth import get_user_id, requires_auth
from src.integrations.msal import get_sign_in_flow, get_token_from_code

subscribe_blueprint = Blueprint("subscribe", __name__)
api = Api(subscribe_blueprint)

manual_global_session = None

class Outlook(Resource):

    @cross_origin()
    def get(self: Any) -> Any:

        global manual_global_session
        code = request.args.get('code')

        # If this is a request from the front end then start the authorisation flow and
        # respond back with the authentication URL that the FE must redirect to.
        if code is None:

            # This is actually how this route is protected, this line will fail with
            # an auth error if no authentication is provided, whilst leaving the rest of
            # the subscription open for microsoft to respond to.
            id = get_user_id()

            flow = get_sign_in_flow()
            manual_global_session = {'flow': flow, 'user': id}
            return {'auth_endpoint': flow['auth_uri']}, 200

        # Otherwise, it's a response from Microsoft, so process the response, combine it
        # with the saved flow and complete the authentication.
        else:
            flow = manual_global_session['flow']
            user = manual_global_session['user']

            integration_object = get_token_from_code(request, flow)
            im.add_integration(user, "msal", integration_object)

            return redirect("http://localhost:3000/")


class Subscribe(Resource):
    """This route responds with a list of all the integrations that the user is currently connected to."""

    @requires_auth
    def get(self):
        """
        Return a list of integrations that the user is connected to.

        Returns:
            list: A list of strings, each referring to a particular integration.

        """
        id = get_user_id()

        # Get the user integration information, this will fail with a KeyError if the user isn't
        # found, which is possible if the user hasn't created any integrations yet.
        try:
            return im.list_integrations(id), 200
        except KeyError:
            return [], 200


api.add_resource(Outlook, "/subscribe/outlook")
api.add_resource(Subscribe, "/subscribe")