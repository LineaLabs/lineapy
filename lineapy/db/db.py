from typing import List

from lineapy.data.graph import Graph
from lineapy.data.types import Node, NodeType, LineaID, SessionContext, DirectedEdge
from lineapy.db.caching_layer.decider import caching_decider

from lineapy.db.base import LineaDBReader, LineaDBWriter, LineaDBConfig

from lineapy.db.asset_manager.base import DataAssetManager

from lineapy.db.relational.schema.relational import (
    ArgumentNodeORM,
    CallNodeORM,
    NodeORM,
    Base,
)

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine


class LineaDB(LineaDBReader, LineaDBWriter):
    """
    - Note that LineaDB coordinates with assset manager and relational db.
      - The asset manager deals with binaries (e.g., cached values) - the relational db deals with more structured data, such as the Nodes and edges.
    - Also, at some point we might have a "cache" such that the readers don't have to go to the database if it's already ready, but that's lower priority
    """

    def __init__(self, config: LineaDBConfig):
        # TODO: we eventually need some configurations
        engine = create_engine(config.database_uri, echo=True)
        self.session = scoped_session(sessionmaker())
        self.session.configure(bind=engine)
        Base.metadata.create_all(engine)

    @staticmethod
    def get_orm(node: Node) -> NodeORM:
        pydantic_to_orm = {
            NodeType.ArgumentNode: ArgumentNodeORM,
            NodeType.CallNode: CallNodeORM,
        }

        return pydantic_to_orm[node.node_type]

    """
    Writers
    """

    def data_asset_manager(self) -> DataAssetManager:
        pass

    def write_context(self, context: SessionContext) -> None:
        pass

    def write_edges(self, edges: List[DirectedEdge]) -> None:
        pass

    def write_nodes(self, nodes: List[Node]) -> None:
        for n in nodes:
            self.write_single_node(n)

    def write_single_node(self, node: Node) -> None:
        node_orm = LineaDB.get_orm(node)(**node.dict())

        self.session.add(node_orm)
        self.session.commit()

        # basic caching logic
        # if caching_decider(node):
        #     self.data_asset_manager.write_node_value(node)

    def add_node_id_to_artifact_table(self, node_id: LineaID):
        """
        Given that whether something is an artifact is just a human annotation, we are going to _exclude_ the information from the Graph Node types and just have a table that tracks what Node IDs are deemed as artifacts.
        """
        # @dhruv TODO:
        # - check node type: should just be CallNode and FunctionDefinitionNode
        #
        # - then insert into a table that's literally just the NodeID and maybe a timestamp for when it was registered as artifact
        raise NotImplementedError

    def remove_node_id_from_artifact_table(self, node_id: LineaID):
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
        query_obj = self.session.query(NodeORM).filter(NodeORM.id == linea_id).one()
        return Node.from_orm(query_obj)

    # fill out the rest based on base.py
    def get_graph_from_artifact_id(self, node: LineaID) -> Graph:
        """
        - This is program slicing over database data.
        - There are lots of complexities when it comes to mutation
          - Examples:
            - Third party libraries have functions that mutate some global or variable state.
          - Strategy for now
            - definitely take care of the simple cases, like `VariableAliasNode`
            - simple heuristics that may create false positives (include things not necessary)
            - but definitely NOT false negatives (then the program CANNOT be executed)
        """

        raise NotImplementedError
