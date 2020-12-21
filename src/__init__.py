# db/__init__.py

import os

from flask import Flask, jsonify
from flask_restx import Resource, Api


def create_app(script_info=None):

    # Instantiate the app.
    app = Flask(__name__)

    # Set config.
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # register blueprints
    from src.api.ping import ping_blueprint
    app.register_blueprint(ping_blueprint)

    # Shell context for flask cli.
    @app.shell_context_processor
    def ctx():
        return {'app': app}

    return app
