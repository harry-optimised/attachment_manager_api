# db/__init__.py

import json
import os
import pathlib

from flask import Flask

from src.dynamodb.connection_manager import ConnectionManager

cm = ConnectionManager()


def create_app(script_info=None):

    # Instantiate the app.
    app = Flask(__name__)

    # Set config.
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    # Setup the database.
    endpoint_url = app.config["DATABASE_URL"]
    region = app.config["AWS_DEFAULT_REGION"]
    cm.initialise(endpoint_url, region)

    # If not running in production, create and seed the table using local files.
    if not app.config["PRODUCTION"]:

        # Create the table.
        schema_json = pathlib.Path().cwd() / "src/dynamodb/files_table_schema.json"
        schema = json.load(open(str(schema_json), "r"))
        cm.create_table(schema)

        # Seed the database.
        seed_json = pathlib.Path().cwd() / "src/tests/seed_data.json"
        seed_data = json.load(open(str(seed_json), "r"))
        cm.seed_db(seed_data)

    # register blueprints
    from src.api.ping import ping_blueprint
    from src.api.files import files_blueprint

    app.register_blueprint(ping_blueprint)
    app.register_blueprint(files_blueprint)

    # Shell context for flask cli.
    @app.shell_context_processor
    def ctx():
        return {"app": app, "cm": cm}

    return app
