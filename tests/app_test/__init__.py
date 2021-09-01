import sys

from config_stub import TestConfig, DevConfig
from flask import Flask
from flask_cors import CORS
from app_db_stub import init_db


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

        import routes_stub

        app.register_blueprint(routes_stub.routes_blueprint)
        return app
