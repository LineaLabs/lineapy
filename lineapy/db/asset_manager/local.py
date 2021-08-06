from lineapy.data.types import NodeValue, Node
from lineapy.db.asset_manager.base import DataAssetManager


class LocalDataAssetManager(DataAssetManager):
    """
    TODO reads from and writes to a local file system.
    """

    def write_node_value(self, node: Node) -> str:
        # TODO
        ...

    def read_node_value(self, uuid: str) -> NodeValue:
        # TODO
        ...
