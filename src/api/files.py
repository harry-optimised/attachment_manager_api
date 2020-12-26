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

    def post(self):
        post_data = request.get_json()
        new_files = post_data.get('files')
        files = cm.get_files_for_user("harry")
        files = {f['reference']: f for f in files}
        response_states = {}
        for f in new_files:
            reference = f['name'] + f['created']
            f['reference'] = reference
            response_states[reference] = 'CREATED' if reference not in files.keys() else 'UPDATED'
            cm.put_file(f)  # This shouldn't fail.

        # Todo: Handle delayed processing with a callback.
        # Todo: Validate type, headers, and schema.
        return {'response_states': response_states}, 200

    def delete(self):
        post_data = request.get_json()
        new_files = post_data.get('files')
        files = cm.get_files_for_user("harry")
        files = {f['reference']: f for f in files}
        response_states = {}
        for f in new_files:
            reference = f['name'] + f['created']
            f['reference'] = reference
            if reference in files.keys():
                cm.delete_file(f) # Should not fail.
                response_states[reference] = 'DELETED'
            else:
                response_states[reference] = 'NOT_FOUND'

        # Todo: Handle delayed processing with a callback.
        # Todo: Validate type, headers, and schema.
        return {'response_states': response_states}, 200

api.add_resource(FilesList, "/files")
