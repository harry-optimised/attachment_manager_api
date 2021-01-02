"""Define the Files API Resource."""

from typing import Any

from flask import Blueprint, abort, request
from flask_restx import Api, Resource
from marshmallow import INCLUDE, Schema, fields

from src import cm
from src.auth import get_user_id, requires_auth

files_blueprint = Blueprint("files", __name__)
api = Api(files_blueprint)


class File(Schema):
    """Validation schema for individual file objects in the list of files."""

    class Meta:
        """Meta."""

        unknown = INCLUDE

    name = fields.Str(required=True)
    created = fields.DateTime(required=True)


class FilesSchema(Schema):
    """Validation schema for files put request."""

    files = fields.Nested(File, many=True, required=True)


class FilesList(Resource):
    """Files API Resource for getting, putting, and deleting files."""

    def _scrub_files(self: Any, files: list) -> list:
        """Remove user and reference properties from each file."""
        scrubbed_files = []
        for f in files:
            _scrubbed = f
            del _scrubbed["user"]
            del _scrubbed["reference"]
            scrubbed_files.append(_scrubbed)
        return scrubbed_files

    @requires_auth
    def get(self: Any) -> Any:
        """Get all files from the database that belong to the authenticated user."""
        id = get_user_id()
        files = cm.get_files(id)
        response_object = {"files": self._scrub_files(files)}
        return response_object, 200

    @requires_auth
    def put(self: Any) -> Any:
        """Add or update a list of provided files in the database for the authenticated user."""
        # Validate request type.
        if request.content_type != "application/json":
            abort(400, "Content Type must be 'application/json'.")

        # Validate the request.
        errors = FilesSchema().validate(request.json)
        if errors:
            abort(400, str(errors))

        # Get user.
        id = get_user_id()

        # Get the list of new files.
        post_data = request.get_json()
        new_files = post_data.get("files")

        # Add all new files to the data base.
        status = {}
        for f in new_files:
            status[f["name"]] = cm.put_file(id, f)

        return {"status": status}, 200

    @requires_auth
    def delete(self: Any) -> Any:
        """Delete a list of provided files from the database for the authenticated user."""
        # Validate request type.
        if request.content_type != "application/json":
            abort(400, "Content Type must be 'application/json'.")

        # Validate the request.
        errors = FilesSchema().validate(request.json)
        if errors:
            abort(400, str(errors))

        # Get user.
        id = get_user_id()

        # Get the list of files to delete.
        post_data = request.get_json()
        new_files = post_data.get("files")

        status = {}
        for f in new_files:
            status[f["name"]] = cm.delete_file(id, f)

        return {"status": status}, 200


api.add_resource(FilesList, "/files")
