"""Define app wide configuration options."""

import os


class BaseConfig:
    """Base configuration options."""

    PRODUCTION = False
    SEED = False
    AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
    DATABASE_URL = os.getenv("DATABASE_URL")


class DevelopmentConfig(BaseConfig):
    """Development configuration options."""

    SEED = False


class ProductionConfig(BaseConfig):
    """Production configuration options."""

    PRODUCTION = True
