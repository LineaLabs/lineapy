from abc import ABC, abstractmethod

from lineapy.data.types import Node, NodeValue, NodeType, LineaID


class DataAssetManager(ABC):
    @abstractmethod
    def write_node_value(self, node: Node) -> str:
        """
        :param node: node whose value is to be materialized.
        :return: URN for the location the node value is written to.
        """
        ...

    @abstractmethod
    def read_node_value(self, id: LineaID) -> NodeValue:
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

    # right now it's just a simple function that returns true if the callnode has an assignment, but in the future we should definitely add more logic
    @staticmethod
    def caching_decider(node: Node):
        if node.node_type == NodeType.CallNode:
            if hasattr(node, "assigned_variable_name"):
                return True
        return False
