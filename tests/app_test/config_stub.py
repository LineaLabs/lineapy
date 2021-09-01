"""Flask configuration."""
from os import environ

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base config."""

    # SECRET_KEY = environ.get("SECRET_KEY")
    pass


class ProdConfig(Config):
    FLASK_ENV = "production"
    DEBUG = False
    TESTING = False
    DATABASE_URI = environ.get("PROD_DATABASE_URI")


class DevConfig(Config):
    FLASK_ENV = "development"
    DEBUG = True
    TESTING = False
    DATABASE_URI = environ.get("DEV_DATABASE_URI")


class TestConfig(Config):
    FLASK_ENV = "development"
    DEBUG = True
    TESTING = True  # better error reports
    DATABASE_URI = environ.get("TEST_DATABASE_URI")
