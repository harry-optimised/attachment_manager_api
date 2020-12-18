# db/__init__.py

import os

from flask import Flask, jsonify
from flask_restx import Resource, Api
from flask_sqlalchemy import SQLAlchemy

# Setup the database.
db = SQLAlchemy()

def create_app(script_info=None):

    # Instantiate the app.
    app = Flask(__name__)

    # Set config.
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # Set up extensions.
    db.init_app(app)

    # register blueprints
    from src.api.ping import ping_blueprint
    app.register_blueprint(ping_blueprint)

    from src.api.users import users_blueprint
    app.register_blueprint(users_blueprint)

    # Shell context for flask cli.
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app
