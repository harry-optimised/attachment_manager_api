"""Define the Synchronise API Resource."""

from flask import Blueprint
from flask_restx import Api

from src.api.synchronisations.outlook import Outlook
from src.api.synchronisations.gmail import Gmail

synchronise_blueprint = Blueprint("synchronise", __name__)
api = Api(synchronise_blueprint)

api.add_resource(Outlook, "/synchronise/outlook")
api.add_resource(Gmail, "/synchronise/gmail")