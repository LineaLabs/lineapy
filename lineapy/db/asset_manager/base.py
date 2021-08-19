from abc import ABC, abstractmethod

from lineapy.data.types import Node, NodeValue


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
        This methods needs to be able to look up a mapping between
        the uuids and the URNs for the serialized results.

        Alternatively, can take the URN as the input
        and have the caller manage the mapping.

        TODO: decide what the input should be.

        :param uuid: uuid for the node whose value is to be retrieved
        :return: the value associated with the node with uuid.
        """
        ...
