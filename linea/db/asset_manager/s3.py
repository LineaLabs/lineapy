from linea import Node
from linea.dataflow.data_types import NodeValue
from linea.db.asset_manager.base import DataAssetManager


class S3DataAssetManager(DataAssetManager):
    """
    TODO reads from and writes to an S3 bucket.
    """

    def write_node_value(self, node: Node) -> str:
        # TODO
        ...

    def read_node_value(self, uuid: str) -> NodeValue:
        # TODO
        ...
