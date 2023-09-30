# pylint: disable=C0413
from flask import Flask
from app.config import Config as config_class
from app.exceptions import CustomException, handle_custom_exception
from app.extensions import ma


print("Starting application")
app = Flask(__name__)
app.config.from_object(config_class)

# Register errors
app.register_error_handler(CustomException, handle_custom_exception)

# Initialize extensions here
ma.init_app(app)

print("Starting threads")
