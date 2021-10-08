import logging
from typing import Optional, cast

from sqlalchemy import and_
from sqlalchemy.orm import scoped_session

from lineapy.constants import DB_DATA_ASSET_MANAGER
from lineapy.data.types import CallNode, LineaID, Node, NodeType, NodeValueType
from lineapy.db.relational.schema.relational import NodeValueORM
from lineapy.utils import get_value_type

logger = logging.getLogger(__name__)


class LocalDataAssetManager:
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
            materialize = isinstance(node, CallNode) and node.value is not None
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
                    start_time=node.start_time,
                    end_time=node.end_time,
                )
                try:
                    self.session.add(value_orm)
                    self.session.commit()
                except Exception:
                    # don't write for now
                    logger.warning(
                        "Had trouble writing value %s, skipping for now.", node
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
