"""Flask configuration variables."""
import os
import logging
from os import path

# from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
# load_dotenv(path.join(basedir, ".env"))


def start_logger():
    logging.basicConfig(
        # filename="scrapper.log",
        level=logging.INFO,
        format="%(levelname)s %(message)s %(asctime)s ",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


class Config:
    """Set Flask configuration from .env file."""

    # General Config
    FLASK_ENV = os.environ.get("FLASK_ENV")

    # Database
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URI")
        or "postgresql://system_user:mypassword@localhost:5432/system_db"
    )

    # Auth
    SECRET_KEY = os.environ.get("SECRET_KEY") or "mysecret"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
