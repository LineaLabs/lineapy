from typing import List

from lineapy.data.graph import Graph
from lineapy.data.types import Node, LineaID
from lineapy.db.caching_layer.decider import caching_decider

from lineapy.db.base import LineaDBReader, LineaDBWriter


class LineaDB(LineaDBReader, LineaDBWriter):
    """
    - Note that LineaDB coordinates with assset manager and relational db.
      - The asset manager deals with binaries (e.g., cached values) - the relational db deals with more structured data, such as the Nodes and edges.
    - Also, at some point we might have a "cache" such that the readers don't have to go to the database if it's already ready, but that's lower priority
    """

    def __init__(self):
        # TODO: we eventually need some configurations
        pass

    """
    Writers
    """

    def write_nodes(self, nodes: List[Node]) -> None:
        for n in nodes:
            self.write_single_node(n)

    def write_single_node(self, node: Node) -> None:
        # @dhruv, first TODO, use SQLAchemy to write---you can directly use the types defined in types.py and no need to redefine them (thanks to Pydantic)

        # basic caching logic
        if caching_decider(node):
            self.data_asset_manager.write_node_value(node)

    def write_node_is_artifact(self, node_id: LineaID):
        """
        Given that whether something is an artifact is just a human annotation, we are going to _exclude_ the information from the Graph Node types and just have a table that tracks what Node IDs are deemed as artifacts.
        cc @dorx please review
        """
        # @dhruv TODO:
        # - check node type: should just be CallNode and FunctionDefinitionNode
        #
        # - then insert into a table that's literally just the NodeID and maybe when it was registered as artifact (something like datetime.now())
        raise NotImplementedError

    def write_node_is_no_longer_artifact(self, node_id: LineaID):
        """
        #dhruv TODO
        The opposite of write_node_is_artifact
        - for now we can just delete it directly
        """
        raise NotImplementedError

    """
    Readers
    """

    def get_node_by_id(self, linea_id: LineaID) -> Node:
        """
        Returns the node by looking up the database by ID
        """

        raise NotImplementedError

    # fill out the rest based on base.py
    def get_graph_from_artifact_id(self, node: LineaID) -> Graph:
        """
        This is basically slicing.
        There are some complexities.
        """

        raise NotImplementedError
