from lineapy.constants import ExecutionMode
from lineapy.db.base import get_default_config_by_environment
from lineapy.db.relational.db import RelationalLineaDB

lineadb = RelationalLineaDB()


def init_db(app):
    print("🛠", app.config)
    db_config = get_default_config_by_environment(ExecutionMode.DEV)
    lineadb.init_db(db_config)
    # TODO: set LineaDBConfig to be app.config
