# db/__init__.py

import os

from flask import Flask, jsonify
from flask_restx import Resource, Api

from src.dynamodb.connection_manager import ConnectionManager

def create_app(script_info=None):

    # Instantiate the app.
    app = Flask(__name__)

    # Set config.
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # Setup the database.
    endpoint_url = app.config['DATABASE_URL']
    region = app.config['AWS_REGION']
    cm = ConnectionManager(endpoint_url, region)

    # register blueprints
    from src.api.ping import ping_blueprint
    app.register_blueprint(ping_blueprint)

    # Shell context for flask cli.
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'cm': cm}

    return app
