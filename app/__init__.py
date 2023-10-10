import logging
import threading
from flask import Flask

from app.config import Config as config_class, create_credentials_json, start_logger
from app.exceptions import CustomException, handle_custom_exception
from app.scrappers.company_csv.main import company_orchestrator
from app.scrappers.g2crowd.main import g2crowd_orchestrator
from app.scrappers.google_drive.main import google_drive_orchestrator


app = Flask(__name__)
app.config.from_object(config_class)
start_logger()
create_credentials_json()

logging.info("Starting application")

app.register_error_handler(CustomException, handle_custom_exception)

logging.info("Starting threads")

company_thread = threading.Thread(
    target=company_orchestrator,
    args=("united states", "companies_input.csv"),
    name="CompanyThread",
)
crowd2url_thread = threading.Thread(target=g2crowd_orchestrator, name="Crowd2UrlThread")
# Define your natural language query
NATURAL_QUERY = "FILENAME Currículo, TEXT Guedes"
google_drive_thread = threading.Thread(
    target=google_drive_orchestrator,
    args=(NATURAL_QUERY,),
    name="GoogleDriveThread",
)
company_thread.start()
crowd2url_thread.start()
google_drive_thread.start()
