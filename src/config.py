"""Define app wide configuration options."""

import os


class BaseConfig:
    """Base configuration options."""

    # Mode Config
    PRODUCTION = False
    SEED = False
    TESTING = False

    # Session Config
    SECRET_KEY = "oh_so_secret"

    # CORS Config
    CORS_HEADERS = "Content-Type"

    # DynamoDB Config
    AWS_DEFAULT_REGION = "eu-west-2"
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Auth Config
    AUTH_TENANT_URL = "https://thea-tenant.eu.auth0.com"
    AUTH_JWT_AUDIENCE = "https://thea-core.com/api"

    # MSAL Config
    MSAL_APP_ID = os.getenv("MSAL_APP_ID")
    MSAL_APP_SECRET = os.getenv("MSAL_APP_SECRET")
    MSAL_REDIRECT = os.getenv("MSAL_REDIRECT")
    MSAL_SCOPES = ["mail.read"]
    MSAL_AUTHORITY = "https://login.microsoftonline.com/common"

    # Microsoft Outlook Graph API Config
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
