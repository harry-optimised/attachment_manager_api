# src/api/files.py

from flask import Blueprint, request
from flask_restx import Api, Resource

from src import cm

files_blueprint = Blueprint("files", __name__)
api = Api(files_blueprint)


class FilesList(Resource):
    def get(self):
        files = cm.get_files_for_user("harry")
        response_object = {
            'files': files
        }
        return response_object, 200

    # Todo: Add marshal with.
    # Todo: Add query validation.

api.add_resource(FilesList, "/files")
