# src/dynamodb/connection_manager.py

from .db_setup import get_dynamodb_connection

class ConnectionManager:

    def __init__(self, endpoint_url, region):
        self.db = get_dynamodb_connection(endpoint_url, region)

