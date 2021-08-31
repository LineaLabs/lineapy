from lineapy.db.db import LineaDB
from lineapy.db.base import LineaDBConfig


def init_db(app):
    print("🛠", app.config)
    # TODO: pass app.config into LineaDBConfig
    global lineadb
    lineadb = LineaDB(LineaDBConfig())
