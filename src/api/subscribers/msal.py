
import msal
import os
import time

from src import app_config


def load_cache(request):
  # Check for a token cache in the session
  cache = msal.SerializableTokenCache()

  return cache


def get_msal_app(cache=None):
  # Initialize the MSAL confidential client
  auth_app = msal.ConfidentialClientApplication(
    app_config['MSAL_APP_ID'],
    authority=app_config['MSAL_AUTHORITY'],
    client_credential=app_config['MSAL_APP_SECRET'],
    token_cache=cache)

  return auth_app

# Method to generate a sign-in flow
def get_sign_in_flow():
  auth_app = get_msal_app()

  return auth_app.initiate_auth_code_flow(
    app_config['MSAL_SCOPES'],
    redirect_uri=app_config['MSAL_REDIRECT'])

# Method to exchange auth code for access token
def get_token_from_code(request, flow):
  cache = load_cache(request)
  auth_app = get_msal_app(cache)
  result = auth_app.acquire_token_by_auth_code_flow(flow, dict(request.args))
  return result