"""Define app wide configuration options."""

import os


class BaseConfig:
    """Base configuration options."""

    SECRET_KEY = "oh_so_secret"
    CORS_HEADERS = 'Content-Type'
    SESSION_TYPE = 'filesystem'

    PRODUCTION = False
    SEED = False
    TESTING = False
    AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
    DATABASE_URL = os.getenv("DATABASE_URL")

    AUTH_TENANT_URL = "https://thea-tenant.eu.auth0.com"
    AUTH_JWT_AUDIENCE = "https://thea-core.com/api"

    MSAL_APP_ID = "42a46086-81ff-4654-8b30-2eb1b4ea551b"
    MSAL_APP_SECRET = "WYweb1osVN_5rCo-Gb.q_A2~UI50Ey.2X4"
    MSAL_REDIRECT = "http://localhost:5000/subscribe/outlook"
    MSAL_SCOPES = ["mail.read"]
    MSAL_AUTHORITY = "https://login.microsoftonline.com/common"


class DevelopmentConfig(BaseConfig):
    """Development configuration options."""

    SEED = False


class TestingConfig(BaseConfig):
    """Testing configuration options."""

    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration options."""

    PRODUCTION = True
