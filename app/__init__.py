import threading
from flask import Flask

# Extensions
from app.config import Config as config_class
from app.exceptions import CustomException, handle_custom_exception
from app.extensions import ma

# Scrappers
from app.scrappers.company_csv.main import company_thread
from app.scrappers.g2crowd.main import task3
from app.scrappers.google_drive.main import task1

app = Flask(__name__)
app.config.from_object(config_class)

# Register errors
app.register_error_handler(CustomException, handle_custom_exception)
# Initialize extensions here
ma.init_app(app)

print("Starting threads")
thread1 = threading.Thread(target=task1)
company_thread = threading.Thread(target=company_thread)
thread3 = threading.Thread(target=task3)

thread1.start()
company_thread.start()
thread3.start()
