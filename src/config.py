"""Define app wide configuration options."""

import os


class BaseConfig:
    """Base configuration options."""

    SECRET_KEY = "oh_so_secret"
    CORS_HEADERS = "Content-Type"
    SESSION_TYPE = "filesystem"

    PRODUCTION = False
    SEED = False
    TESTING = False
    AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
    DATABASE_URL = os.getenv("DATABASE_URL")

    AUTH_TENANT_URL = "https://thea-tenant.eu.auth0.com"
    AUTH_JWT_AUDIENCE = "https://thea-core.com/api"

    MSAL_APP_ID = "b56b6ea3-6322-415e-a9b3-72ab82fc4169"
    MSAL_APP_SECRET = "edKOV9_NBkJ1-7oUI5F_mDRkxP7ko.hPmq"
    MSAL_REDIRECT = "http://localhost:5000/subscribe/outlook"
    MSAL_SCOPES = ["mail.read"]
    MSAL_AUTHORITY = "https://login.microsoftonline.com/common"

    GRAPH_API_REQUEST_LIMIT = 100


class DevelopmentConfig(BaseConfig):
    """Development configuration options."""

    SEED = False


class TestingConfig(BaseConfig):
    """Testing configuration options."""

    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration options."""

    PRODUCTION = True


# Dispatch the config to a variable accessible app-wide.
configs = {
    "src.config.DevelopmentConfig": DevelopmentConfig,
    "src.config.TestingConfig": TestingConfig,
    "src.config.ProductionConfig": ProductionConfig,
}
app_config = {**vars(BaseConfig), **vars(configs[os.getenv("APP_SETTINGS")])}
