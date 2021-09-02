from flask import Flask
from flask_cors import CORS

from lineapy.app.app_db import init_db
from lineapy.app.config import TestConfig, DevConfig


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_object(DevConfig())

    with app.app_context():

        init_db(app)

        from lineapy.app.routes import routes_blueprint

        app.register_blueprint(routes_blueprint)
        return app


app = create_app()
if __name__ == "__main__":
    app.run(port=4000)
