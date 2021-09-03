from flask import Flask
from flask_cors import CORS

from lineapy.app.app_db import init_db
import config


def create_app(mode):
    app = Flask(__name__)
    CORS(app)

    if mode == "DEV":
        app.config["ENV"] = config.DEV_ENV
        app.config["DEBUG"] = config.DEV_DEBUG
        app.config["TESTING"] = config.DEV_TESTING
        app.config["DATABASE_URI"] = config.DEV_DATABASE_URI
    elif mode == "TEST":
        app.config["ENV"] = config.TEST_ENV
        app.config["DEBUG"] = config.TEST_DEBUG
        app.config["TESTING"] = config.TEST_TESTING
        app.config["DATABASE_URI"] = config.TEST_DATABASE_URI
    elif mode == "PROD":
        app.config["ENV"] = config.PROD_ENV
        app.config["DEBUG"] = config.PROD_DEBUG
        app.config["TESTING"] = config.PROD_TESTING
        app.config["DATABASE_URI"] = config.PROD_DATABASE_URI

    with app.app_context():
        init_db(app)

        from lineapy.app.routes import routes_blueprint

        app.register_blueprint(routes_blueprint)
        return app


if __name__ == "__main__":
    app = create_app("DEV")
    app.run(port=4000)
