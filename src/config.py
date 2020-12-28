"""Define app wide configuration options."""

import os


class BaseConfig:
    """Base configuration options."""

    PRODUCTION = False
    SEED = False
    TESTING = False
    AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
    DATABASE_URL = os.getenv("DATABASE_URL")

    AUTH_TENANT_URL = "https://thea-tenant.eu.auth0.com"
    AUTH_JWT_AUDIENCE = "https://thea-core.com/api"


class DevelopmentConfig(BaseConfig):
    """Development configuration options."""

    SEED = True


class TestingConfig(BaseConfig):
    """Testing configuration options."""

    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration options."""

    PRODUCTION = True
