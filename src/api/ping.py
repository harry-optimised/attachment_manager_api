"""Define the ping API resource."""

from typing import Any

from flask import Blueprint
from flask_restx import Api, Resource

ping_blueprint = Blueprint("ping", __name__)
api = Api(ping_blueprint)


class Ping(Resource):
    """Ping resource for checking API health."""

    def get(self: Any) -> dict:
        """Return pong message."""
        return {"status": "success", "message": "pong!"}


api.add_resource(Ping, "/ping")
