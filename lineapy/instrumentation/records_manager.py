from typing import Any, List, Union
from lineapy.data.types import Node, DirectedEdge

# from lineapy.db.

# TODO: add another ORM type where it's just the ID and the table.

RecordType = Union[Node, DirectedEdge]


class RecordsManager:
    def __init__(self):
        self.records_pool: List[RecordType] = []
        # instantiate a connection to LineaDB
        # TODO, need to wait until the linea-db-spec is merged and everything
        # self.db = LineaDB()

    def add_node(self, record: RecordType):
        pass

    def flush_records_and_close(self):
        """
        To ensure that the records are sent to the DB and that the db instanced is closed
        """
        pass
