from abc import ABC, abstractmethod

from linea.data.types import Node, NodeValue


class DataAssetManager(ABC):

    @abstractmethod
    def write_node_value(self, node: Node) -> str:
        """
        :param node: node whose value is to be materialized.
        :return: URN for the location the node value is written to.
        """
        ...

    @abstractmethod
    def read_node_value(self, uuid: str) -> NodeValue:
        """
        :param uuid: uuid for the node whose value is to be retrieved
        :return: the value associated with the node with uuid.
        """
        ...
