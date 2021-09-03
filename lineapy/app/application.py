from flask import Flask
from flask_cors import CORS
import toml
import os.path as path

from lineapy.app.app_db import init_db
import config


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config["ENV"] = config.DEV_ENV
    app.config["DEBUG"] = config.DEV_DEBUG
    app.config["TESTING"] = config.DEV_TESTING
    app.config["DATABASE_URI"] = config.DEV_DATABASE_URI

    with app.app_context():
        init_db(app)

        from lineapy.app.routes import routes_blueprint

        app.register_blueprint(routes_blueprint)
        return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=4000)
