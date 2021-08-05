from typing import Any

from linea.db.relational.base import RelationalLineaDB


class SQLiteLineaDB(RelationalLineaDB):
    @property
    def connection(self) -> Any:
        # TODO
        pass
