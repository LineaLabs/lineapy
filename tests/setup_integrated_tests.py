from lineapy.db.base import LineaDBConfig
from lineapy.db.relational.db import RelationalLineaDB
from tests.test_flask_app import setup_db

setup_db("DEV")
