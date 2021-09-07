from flask import Flask
from flask_cors import CORS

from lineapy import constants
from lineapy.app.app_db import init_db


def create_app(mode):
    app = Flask(__name__)
    CORS(app)

    if mode == "DEV":
        app.config["ENV"] = constants.DEV_ENV
        app.config["DEBUG"] = constants.DEV_DEBUG
        app.config["TESTING"] = constants.DEV_TESTING
        app.config["DATABASE_URI"] = constants.DEV_DATABASE_URI
    elif mode == "TEST":
        app.config["ENV"] = constants.TEST_ENV
        app.config["DEBUG"] = constants.TEST_DEBUG
        app.config["TESTING"] = constants.TEST_TESTING
        app.config["DATABASE_URI"] = constants.TEST_DATABASE_URI
    elif mode == "PROD":
        app.config["ENV"] = constants.PROD_ENV
        app.config["DEBUG"] = constants.PROD_DEBUG
        app.config["TESTING"] = constants.PROD_TESTING
        app.config["DATABASE_URI"] = constants.PROD_DATABASE_URI

    with app.app_context():
        init_db(app)

        from lineapy.app.routes import routes_blueprint

        app.register_blueprint(routes_blueprint)
        return app


if __name__ == "__main__":
    app = create_app("DEV")
    app.run(port=4000)
