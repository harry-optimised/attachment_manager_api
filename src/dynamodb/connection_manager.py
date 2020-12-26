"""Define the connection manager for managing connections to the dynamo database."""

import json
import pathlib
from typing import Any

from boto3.dynamodb.conditions import Key

from .db_setup import get_dynamodb_connection


class ConnectionManager:
    """Manages the connection to the dynamo database."""

    def __init__(self: Any) -> None:
        """Initialise so that this object can be created before it is initialised."""
        pass

    def initialise(self: Any, app_config: dict) -> bool:
        """Initialise the connection to the database and table."""
        # Pull out the bits we care about so we fail early.
        endpoint_url = app_config["DATABASE_URL"]
        region = app_config["AWS_DEFAULT_REGION"]
        in_production = app_config["PRODUCTION"]
        do_seed = app_config["SEED"]

        self.db = get_dynamodb_connection(endpoint_url, region)

        # If we're NOT running in production, create and seed the table using local files.
        if not in_production:

            # Create the table.
            schema_json = pathlib.Path().cwd() / "src/dynamodb/files_table_schema.json"
            schema = json.load(open(str(schema_json), "r"))
            self.files_table = self._create_table(schema)

            # Seed the database, we only seed in development mode.
            if do_seed:
                seed_json = pathlib.Path().cwd() / "src/tests/seed_data.json"
                seed_data = json.load(open(str(seed_json), "r"))
                self.seed_db(seed_data)

        # Otherwise, we try and load the production table.
        else:
            self.files_table = self.db.Table("FilesTable")

        return True

    def _create_table(self: Any, table_schema: dict) -> Any:
        """Create a table in the database using the provided schema and return it."""
        try:
            return self.db.create_table(
                TableName=table_schema["TableName"],
                KeySchema=table_schema["KeySchema"],
                AttributeDefinitions=table_schema["AttributeDefinitions"],
                ProvisionedThroughput=table_schema["ProvisionedThroughput"],
            )
        except Exception as e:
            if e.__class__.__name__ == "ResourceInUseException":
                return self.db.Table("FilesTable")
            else:
                raise e

    def seed_db(self: Any, seed_data: list) -> bool:
        """Add all items in the provided list to the table, do no validation checks."""
        for item in seed_data:
            self.files_table.put_item(Item=item)
        return True

    def scan_db(self: Any) -> list:
        """Return all files in the database."""
        all_items = self.files_table.scan()
        return all_items["Items"]

    def get_files(self: Any, user: str) -> list:
        """Get all files from the database belonging to the specified user."""
        response = self.files_table.query(
            KeyConditionExpression=Key("user").eq(user), ConsistentRead=True
        )
        return response["Items"]

        # Todo: Generalise to multiple batches, see LastEvaluatedKey.

    def put_file(self: Any, user: str, file: str) -> bool:
        """Add a file to the database for the specified user."""
        # To create the reference, we need name and created properties.
        assert "name" in file.keys()
        assert "created" in file.keys()

        # Create and add the reference and user.
        file["reference"] = file["name"] + file["created"]
        file["user"] = user

        self.files_table.put_item(Item=file)
        return True

    def delete_file(self: Any, user: str, file: dict) -> bool:
        """Delete a single file from the database belonging to the specified user."""
        # To create the reference, we need name and created properties.
        assert "name" in file.keys()
        assert "created" in file.keys()

        reference = file["name"] + file["created"]

        self.files_table.delete_item(Key={"user": user, "reference": reference})
        return True
