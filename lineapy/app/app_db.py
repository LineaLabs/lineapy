from lineapy.db.base import LineaDBConfig
from lineapy.db.relational.db import RelationalLineaDB

lineadb = RelationalLineaDB(LineaDBConfig())


def init_db(app):
    print("🛠", app.config)
    # TODO: set LineaDBConfig to be app.config
