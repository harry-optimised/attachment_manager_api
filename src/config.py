# db/config.py

import os

class BaseConfig:
    TESTING = False
    AWS_REGION = "eu-west-2"
    DATABASE_URL = "http://localhost:8000"

class DevelopmentConfig(BaseConfig):
    pass

class TestingConfig(BaseConfig):
    TESTING = True
    pass

class ProductionConfig(BaseConfig):
    pass

