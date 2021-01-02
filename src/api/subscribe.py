"""Define the Subscribe API Resource."""

from typing import Any

from flask import Blueprint, request, redirect, jsonify, Response
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

        print(request)
        global manual_global_session
        flow = manual_global_session['flow']
        user = manual_global_session['user']
        result = get_token_from_code(request, flow)

        # Store the result.
        result = im.add_integration(user, "msal", result)

        # Todo: Setup a subscription with MSAL for all future messages.

        return redirect("http://localhost:3000/")


    @requires_auth
    @cross_origin()
    def put(self: Any) -> Any:
        # Todo: I get a CORS error on the other end.
        id = get_user_id()
        flow = get_sign_in_flow()
        global manual_global_session
        manual_global_session = {'flow': flow, 'user': id}
        return redirect(flow['auth_uri'])


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