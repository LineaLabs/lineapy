from typing import List

from lineapy.data.types import Node
from lineapy.db.base import LineaDBConfig
from lineapy.db.db import LineaDB

# TODO: add another ORM type where it's just the ID and the table.


class RecordsManager:
    def __init__(self, config: LineaDBConfig):
        self.records_pool: List[Node] = []
        self.db = LineaDB(config)

    def add_evaluated_nodes(self, nodes: List[Node]) -> None:
        self.records_pool += nodes
        return

    def flush_records(self) -> None:
        """
        To ensure that the records are sent to the DB and that the db instanced is closed
        TODO: wrap this in try catch blocks
        """
        self.db.write_nodes(self.records_pool)
        # reset
        self.records_pool = []
        return

    def exit(self):
        self.flush_records()
        # TODO: do we need some DB cleanup code?
        return
