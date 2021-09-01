import sys

from config import TestConfig, DevConfig
from flask import Flask
from flask_cors import CORS
from app_db import init_db


def create_app():
    app = Flask(__name__)
    CORS(app)

    # if hasattr(sys, "_called_from_test"):
    #     print(f"🐍 TEST MODE 🐍")
    #     app.config.from_object(TestConfig())

    # else:
    app.config.from_object(DevConfig())

    init_db(app)

    with app.app_context():

        import routes

        app.register_blueprint(routes.routes_blueprint)
        return app
