"""Factory method for creating and setting up a Flask application."""

import os
from typing import Any

from flask import Flask, jsonify

from src.dynamodb.connection_manager import ConnectionManager

cm = ConnectionManager()
app_config = None


def create_app() -> Any:
    """Create and set up a Flask application."""
    # Instantiate the app.
    app = Flask(__name__)

    # Set config.
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    # Make the app config global so other parts of the system can use it.
    global app_config
    app_config = app.config

    # Setup the database.
    cm.initialise(app.config)

    # Register blueprints
    from src.api.files import files_blueprint
    from src.api.ping import ping_blueprint

    app.register_blueprint(ping_blueprint)
    app.register_blueprint(files_blueprint)

    return app
