"""Define the Synchronise API Resource."""

from flask import Blueprint
from flask_restx import Api

from src.api.synchronisations.outlook import Outlook

synchronise_blueprint = Blueprint("synchronise", __name__)
api = Api(synchronise_blueprint)

api.add_resource(Outlook, "/synchronise/outlook")
