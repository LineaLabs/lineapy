from lineapy.db.db_utils import get_current_time
from typing import List, Optional

from lineapy.data.types import LineaID, Node, SessionContext
from lineapy.db.base import LineaDBConfig
from lineapy.db.relational.db import RelationalLineaDB


# TODO: add another ORM type where it's just the ID and the table.


class RecordsManager:
    def __init__(self, config: LineaDBConfig):
        self.records_pool: List[Node] = []
        self.db = RelationalLineaDB()
        self.db.init_db(config)

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

    """
    Pass through functions to the db
    Maybe we can just expose the db instead, but having a layer of indirection just in cas?
    """

    def write_session_context(self, context: SessionContext) -> None:
        """
        Special casing this since its done once at the beginning
        """
        self.db.write_context(context)

    def add_node_id_to_artifact_table(
        self, node_id: LineaID, description: Optional[str] = None
    ):
        # need to flush all to DB since it's accessing its values at runtime
        self.flush_records()
        date_created = get_current_time()
        self.db.add_node_id_to_artifact_table(node_id, date_created, description)
