from typing import Any

from lineapy.db.relational.base import RelationalLineaDB


class SQLiteLineaDB(RelationalLineaDB):
    @property
    def connection(self) -> Any:
        # TODO
        pass
