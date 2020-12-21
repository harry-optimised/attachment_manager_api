# db/config.py

import os

class BaseConfig:
    TESTING = False
    PRODUCTION = False
    AWS_REGION = "eu-west-2"
    DATABASE_URL = ""

class DevelopmentConfig(BaseConfig):
    DATABASE_URL = "http://db:8000"

class TestingConfig(BaseConfig):
    TESTING = True
    pass

class ProductionConfig(BaseConfig):
    PRODUCTION = True

