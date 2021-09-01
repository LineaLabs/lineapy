import sys

from tests.app_test.config_test import TestConfig, DevConfig
from flask import Flask
from flask_cors import CORS
from tests.app_test.app_db_test import init_db


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

        import routes_test

        app.register_blueprint(routes_test.routes_blueprint)
        return app
