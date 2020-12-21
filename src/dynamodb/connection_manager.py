# src/dynamodb/connection_manager.py

from .db_setup import get_dynamodb_connection

class ConnectionManager:

    def __init__(self, endpoint_url, region):
        self.db = get_dynamodb_connection(endpoint_url, region)

    def create_files_table(self, table_schema):
        """Create a table in the database using the provided schema, ignore if already exists."""
        try:
            table = self.db.create_table(
                TableName=table_schema['TableName'],
                KeySchema=table_schema['KeySchema'],
                AttributeDefinitions=table_schema['AttributeDefinitions'],
                ProvisionedThroughput=table_schema['ProvisionedThroughput']
            )
        except Exception as e:
            if e.__class__.__name__ != "ResourceInUseException":
                raise e

    def seed_db(self, seed_data):
        """Add all items in the provided array to the table, do no validation checks."""
        table = self.db.Table('FilesTable')
        for item in seed_data:
            table.put_item(Item=item)

    def scan_db(self):
        table = self.db.Table('FilesTable')
        all_items = table.scan()
        print(all_items['Items'])
