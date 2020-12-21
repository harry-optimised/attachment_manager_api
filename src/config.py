# db/config.py

import os


class BaseConfig:
    TESTING = False
    PRODUCTION = False
    AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
    DATABASE_URL = os.getenv("DATABASE_URL")


class DevelopmentConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    TESTING = True


class ProductionConfig(BaseConfig):
    PRODUCTION = True
