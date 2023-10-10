"""Flask configuration variables."""
import os
import json
import logging
from os import path

from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))


def start_logger():
    logging.basicConfig(
        # filename="scrapper.log",
        level=logging.INFO,
        format="%(levelname)s %(message)s %(asctime)s ",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


class Config:
    """Set Flask / Google Drive configuration from .env file."""

    load_dotenv(path.join(basedir, ".env"))

    FLASK_ENV = os.environ.get("FLASK_ENV")
    CLIENT_ID = os.environ.get("CLIENT_ID")
    PROJECT_ID = os.environ.get("PROJECT_ID")
    AUTH_URI = os.environ.get("AUTH_URI")
    TOKEN_URI = os.environ.get("TOKEN_URI")
    AUTH_PROVIDER_X509_CERT_URL = os.environ.get("AUTH_PROVIDER_X509_CERT_URL")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    REDIRECT_URLS = os.environ.get("REDIRECT_URLS")


def create_credentials_json():
    logging.info("Creating/Populating credentials.json")
    client_id = Config.CLIENT_ID
    project_id = Config.PROJECT_ID
    auth_uri = Config.AUTH_URI
    token_uri = Config.TOKEN_URI
    auth_provider_x509_cert_url = Config.AUTH_PROVIDER_X509_CERT_URL
    client_secret = Config.CLIENT_SECRET
    redirect_uris = Config.REDIRECT_URLS

    # Define the structure for credentials.json
    credentials_data = {
        "installed": {
            "client_id": client_id,
            "project_id": project_id,
            "auth_uri": auth_uri,
            "token_uri": token_uri,
            "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
            "client_secret": client_secret,
            "redirect_uris": [redirect_uris],
        }
    }

    # Define the path to the google_drive directory and credentials.json
    google_drive_dir = os.path.join(os.path.dirname(__file__), "scrappers/google_drive")
    credentials_path = os.path.join(google_drive_dir, "credentials.json")

    # Serialize the data as JSON and write it to credentials.json
    with open(credentials_path, "w", encoding="utf-8") as credentials_file:
        json.dump(credentials_data, credentials_file, indent=4)
