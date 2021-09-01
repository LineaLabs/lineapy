from lineapy.data.types import NodeValue, Node, LineaID
from lineapy.db.asset_manager.base import DataAssetManager
from lineapy.db.relational.schema.relational import NodeValueORM

from sqlalchemy.orm import scoped_session
from sqlalchemy import and_


class LocalDataAssetManager(DataAssetManager):
    def __init__(self, session: scoped_session):
        self.session = session

    def write_node_value(self, node: Node, version: int) -> str:
        # first check if node value already exists
        if (
            self.session.query(NodeValueORM)
            .filter(
                and_(NodeValueORM.node_id == node.id, NodeValueORM.version == version)
            )
            .first()
            is not None
        ):
            return

        materialize = DataAssetManager.caching_decider(node)
        value = None
        if materialize:
            value = node.value
        value_orm = NodeValueORM(
            node_id=node.id, value=value, version=version, virtual=not materialize
        )
        self.session.add(value_orm)
        self.session.commit()

    def read_node_value(self, id: LineaID) -> NodeValue:
        value_orm = self.session.query(NodeValueORM).filter(NodeValueORM.id == id).one()
        return value_orm.value
