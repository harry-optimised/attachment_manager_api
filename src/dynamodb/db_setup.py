# src/dynamodb/db_setup.py

import boto3
from botocore.config import Config

def get_dynamodb_connection(endpoint_url, region):
    """Instantiate and return a dynamodb resource using boto3."""
    # Create the config.
    config = Config(
        region_name=region,
        signature_version='v4',
        retries={
            'max_attempts': 10,
            'mode': 'standard'
        }
    )

    # Create the connection.
    db = boto3.resource('dynamodb', endpoint_url=endpoint_url, config=config)
    return db