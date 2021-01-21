"""Define the Subscribe API Resource."""

from typing import Any

from flask import Blueprint
from flask_restx import Api, Resource

from src.api.subscriptions.outlook import Outlook
from src.api.subscriptions.gmail import Gmail
from src.auth import get_user_id, requires_auth
from src.integration_manager import im

subscribe_blueprint = Blueprint("subscribe", __name__)
api = Api(subscribe_blueprint)


class Subscribe(Resource):
    """This route responds with a list of all the integrations that the user is currently connected to."""

    @requires_auth
    def get(self: Any) -> Any:
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


api.add_resource(Gmail, "/subscribe/gmail")
api.add_resource(Outlook, "/subscribe/outlook")
api.add_resource(Subscribe, "/subscribe")
