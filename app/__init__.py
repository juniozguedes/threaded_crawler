import threading
from flask import Flask

from app.config import Config as config_class
from app.exceptions import CustomException, handle_custom_exception
from app.extensions import ma

from app.scrappers.company_csv.main import company_thread
from app.scrappers.g2crowd.main import task3
from app.scrappers.google_drive.main import task1

app = Flask(__name__)
app.config.from_object(config_class)

app.register_error_handler(CustomException, handle_custom_exception)
ma.init_app(app)

print("Starting threads")
CSV_INPUT = "companies_input.csv"

thread1 = threading.Thread(target=task1)
company_thread = threading.Thread(target=company_thread(CSV_INPUT))
thread3 = threading.Thread(target=task3)

thread1.start()
company_thread.start()
thread3.start()
