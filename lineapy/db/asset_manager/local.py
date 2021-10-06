from typing import Optional, cast
from pickle import PicklingError
from sqlalchemy import and_
from sqlalchemy.orm import scoped_session

from lineapy.constants import DB_DATA_ASSET_MANAGER
from lineapy.data.types import CallNode, NodeType, NodeValueType, Node, LineaID
from lineapy.db.asset_manager.base import DataAssetManager
from lineapy.db.relational.schema.relational import NodeValueORM
from lineapy.utils import get_value_type, internal_warning_log


class LocalDataAssetManager(DataAssetManager):
    def __init__(self, session: scoped_session):
        self.session = session

    def write_node_value(
        self, node: Node, version: int, graph_cache_veto: bool
    ) -> Optional[str]:
        """
        FIXME: not sure why we are returning DB_DATA_ASSET_MANAGER
        """

        if graph_cache_veto:
            return DB_DATA_ASSET_MANAGER

        if getattr(node, "value", None) is None:
            return DB_DATA_ASSET_MANAGER

        # first check if node value already exists
        if self.is_node_cached(node, version):
            return DB_DATA_ASSET_MANAGER

        if node.node_type == NodeType.CallNode:
            node = cast(CallNode, node)
            materialize = DataAssetManager.caching_decider(node)
            if materialize:
                value = node.value
                value_type = get_value_type(value)
                if value_type is None:
                    return None
                value_orm = NodeValueORM(
                    node_id=node.id,
                    value=value,
                    value_type=get_value_type(value),
                    version=version,
                    virtual=not materialize,
                )
                try:
                    self.session.add(value_orm)
                    self.session.commit()
                except:
                    # don't write for now
                    internal_warning_log(
                        f"Had trouble writing value {node}, skipping for now."
                    )
                return DB_DATA_ASSET_MANAGER
        return None

    def read_node_value(self, id: LineaID, version: int) -> NodeValueType:
        value_orm = (
            self.session.query(NodeValueORM)
            .filter(
                and_(
                    NodeValueORM.node_id == id, NodeValueORM.version == version
                )
            )
            .one()
        )
        return value_orm.value

    def is_node_cached(self, node: Node, version: int):
        return (
            self.session.query(NodeValueORM)
            .filter(
                and_(
                    NodeValueORM.node_id == node.id,
                    NodeValueORM.version == version,
                )
            )
            .first()
            is not None
        )
