"""Factory method for creating and setting up a Flask application."""

import os
from typing import Any

from flask import Flask
from flask_cors import CORS

from src.dynamodb.connection_manager import cm
from src.integration_manager import im


def create_app() -> Any:
    """Create and set up a Flask application."""
    # Instantiate the app.
    app = Flask(__name__)

    # Set config.
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    # Setup CORS.
    CORS(app)

    # Setup the database.
    cm.initialise(app.config)

    # Setup the integration manager.
    im.initialise(cm, app.config)

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
    def add_custom_cors_headers(response: Any) -> Any:
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    return app
