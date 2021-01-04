"""Factory method for creating and setting up a Flask application."""

import pathlib
import os
from typing import Any

from flask import Flask
from flask_cors import CORS

from src.dynamodb.connection_manager import ConnectionManager
from src.integrations.integration_manager import IntegrationManager

app_config = None
cm = ConnectionManager()
im = IntegrationManager(cm)


def create_app() -> Any:
    """Create and set up a Flask application."""
    # Instantiate the app.
    app = Flask(__name__)

    # Set config.
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    # Setup CORS.
    cors = CORS(app)

    # Make the app config global so other parts of the system can use it.
    global app_config
    app_config = app.config

    # Setup the database.
    cm.initialise(app.config)

    # Register blueprints
    from src.api.files import files_blueprint
    from src.api.ping import ping_blueprint
    from src.api.subscribe import subscribe_blueprint
    from src.api.synchronise import synchronise_blueprint

    app.register_blueprint(files_blueprint)
    app.register_blueprint(ping_blueprint)
    app.register_blueprint(subscribe_blueprint)
    app.register_blueprint(synchronise_blueprint)

    @app.after_request
    def add_custom_cors_headers(response):
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    return app
