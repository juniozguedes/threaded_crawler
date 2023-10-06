import logging
import threading
from flask import Flask

from app.config import Config as config_class
from app.exceptions import CustomException, handle_custom_exception

from app.scrappers.company_csv.main import company_thread
from app.scrappers.g2crowd.main import crowd2url_thread
from app.scrappers.google_drive.main import task1


app = Flask(__name__)
app.config.from_object(config_class)

logging.basicConfig(
    # filename="scrapper.log",
    level=logging.INFO,
    format="%(levelname)s %(message)s %(asctime)s ",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.info("Starting application")

app.register_error_handler(CustomException, handle_custom_exception)

logging.info("Starting threads")

# _thread1 = threading.Thread(target=task1)

# I assume that we want to get linkedin results by country
_company_thread = threading.Thread(target=company_thread("united states"))
_crowd2url_thread = threading.Thread(target=crowd2url_thread())

# _thread1.start()
_company_thread.start()
_crowd2url_thread.start()
