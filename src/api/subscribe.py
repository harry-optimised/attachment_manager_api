"""Define the Subscribe API Resource."""

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

subscribe_blueprint = Blueprint("subscribe", __name__)
api = Api(subscribe_blueprint)

manual_global_session = None

class Outlook(Resource):

    @cross_origin()
    def get(self: Any) -> Any:
        global manual_global_session
        flow = manual_global_session['flow']
        user = manual_global_session['user']
        result = get_token_from_code(request, flow)

        # Store the result.
        result = cm.merge_user(user, result, "msal")

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

    @requires_auth
    def get(self):

        # Todo: Have a single /subscribe route that returns all subscriptions the user has.
        # Currently this just checks if an MSAL entry exists for the user, nothing more.
        # Should probably check that the MSAL entry is still valid. In this request or elsewhere?
        id = get_user_id()

        # Todo: What happens if this returns false (user not in database)?
        user = cm.get_user(id)

        if not user:
            return {'integrations': []}, 200

        integrations = []
        if 'msal' in user.keys():
            integrations.append('msal')

        return {'integrations': integrations}, 200

api.add_resource(Outlook, "/subscribe/outlook")
api.add_resource(Subscribe, "/subscribe")