from lineapy.db.base import LineaDBConfig
from lineapy.db.relational.db import RelationalLineaDB

lineadb = RelationalLineaDB()


def init_db(app):
    print("🛠", app.config)
    lineadb.init_db(LineaDBConfig(mode="DEV"))
    # TODO: set LineaDBConfig to be app.config
