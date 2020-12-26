"""Define the Files API Resource."""

from typing import Any

from flask import Blueprint, request
from flask_restx import Api, Resource

from src import cm

files_blueprint = Blueprint("files", __name__)
api = Api(files_blueprint)


class FilesList(Resource):
    """Files API Resource for getting, putting, and deleting files."""

    def get(self: Any) -> Any:
        """Get all files from the database that belong to the authenticated user."""
        # We expect a user query parameter, will be replaced with auth0 soon.
        user = request.args.get("user")
        files = cm.get_files(user)
        response_object = {"files": files}
        return response_object, 200

        # Todo: Add marshal with.
        # Todo: Add query validation.

    def put(self: Any) -> Any:
        """Add or update a list of provided files in the database for the authenticated user."""
        post_data = request.get_json()
        new_files = post_data.get("files")
        user = post_data.get("user")
        files = cm.get_files(user)
        files = {f["reference"]: f for f in files}
        response_states = {}
        for f in new_files:
            reference = f["name"] + f["created"]
            f["reference"] = reference
            response_states[reference] = (
                "CREATED" if reference not in files.keys() else "UPDATED"
            )
            cm.put_file(user, f)  # This shouldn't fail.

        # Todo: Handle delayed processing with a callback.
        # Todo: Validate type, headers, and schema.
        return {"response_states": response_states}, 200

    def delete(self: Any) -> Any:
        """Delete a list of provided files from the database for the authenticated user."""
        post_data = request.get_json()
        new_files = post_data.get("files")
        user = post_data.get("user")
        files = cm.get_files(user)
        files = {f["reference"]: f for f in files}

        response_states = {}
        for f in new_files:
            reference = f["name"] + f["created"]
            f["reference"] = reference
            if reference in files.keys():
                cm.delete_file(user, f)  # Should not fail.
                response_states[reference] = "DELETED"
            else:
                response_states[reference] = "NOT_FOUND"

        # Todo: Handle delayed processing with a callback.
        # Todo: Validate type, headers, and schema.
        return {"response_states": response_states}, 200


api.add_resource(FilesList, "/files")
