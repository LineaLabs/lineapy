from typing import Any, List, Union
from lineapy.data.types import Node, DirectedEdge

# from lineapy.db.

RecordType = Union[Node, DirectedEdge]


class RecordsManager:
    def __init__(self):
        self.records_pool: List[RecordType] = []
        # instantiate a connection to LineaDB
        # TODO
        # self.db = LineaDB()

    def add_to_records_pool(self, record: RecordType):
        pass

    def flush_records_and_close(self):
        """
        To ensure that the records are sent to the DB and that the db instanced is closed
        """
        pass
