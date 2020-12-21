# db/config.py

import os

class BaseConfig:
    TESTING = False

class DevelopmentConfig(BaseConfig):
    pass

class TestingConfig(BaseConfig):
    TESTING = True
    pass

class ProductionConfig(BaseConfig):
    pass

