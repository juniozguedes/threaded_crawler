import logging
import threading
from flask import Flask

from app.config import Config as config_class, start_logger
from app.exceptions import CustomException, handle_custom_exception

from app.scrappers.company_csv.main import company_orchestrator
from app.scrappers.g2crowd.main import g2crowd_orchestrator


app = Flask(__name__)
app.config.from_object(config_class)
start_logger()

logging.info("Starting application")

app.register_error_handler(CustomException, handle_custom_exception)

logging.info("Starting threads")

company_thread = threading.Thread(
    target=company_orchestrator,
    args=("united states", "companies_input.csv"),
    name="CompanyThread",
)
crowd2url_thread = threading.Thread(target=g2crowd_orchestrator, name="Crowd2UrlThread")

company_thread.start()
crowd2url_thread.start()
