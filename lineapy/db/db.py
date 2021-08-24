from typing import List, cast

from lineapy.data.graph import Graph
from lineapy.data.types import *
from lineapy.db.caching_layer.decider import caching_decider

from lineapy.db.base import LineaDBReader, LineaDBWriter, LineaDBConfig

from lineapy.db.asset_manager.base import DataAssetManager

from lineapy.db.relational.schema.relational import *

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import and_


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

        self.session.query(NodeORM).delete()
        self.session.commit()

    @staticmethod
    def get_orm(node: Node) -> NodeORM:
        pydantic_to_orm = {
            NodeType.ArgumentNode: ArgumentNodeORM,
            NodeType.CallNode: CallNodeORM,
            NodeType.ImportNode: ImportNodeORM,
            NodeType.LiteralAssignNode: LiteralAssignNodeORM,
            NodeType.FunctionDefinitionNode: FunctionDefinitionNodeORM,
            NodeType.ConditionNode: ConditionNodeORM,
            NodeType.LoopNode: LoopNodeORM,
            NodeType.DataSourceNode: DataSourceNodeORM,
            NodeType.StateChangeNode: StateChangeNodeORM,
            NodeType.VariableAliasNode: VariableAliasNodeORM,
        }

        return pydantic_to_orm[node.node_type]

    @staticmethod
    def get_pydantic(node: NodeORM) -> Node:
        orm_to_pydantic = {
            NodeType.ArgumentNode: ArgumentNode,
            NodeType.CallNode: CallNode,
            NodeType.ImportNode: ImportNode,
            NodeType.LiteralAssignNode: LiteralAssignNode,
            NodeType.FunctionDefinitionNode: FunctionDefinitionNode,
            NodeType.ConditionNode: ConditionNode,
            NodeType.LoopNode: LoopEnterNode,
            NodeType.DataSourceNode: DataSourceNode,
            NodeType.StateChangeNode: StateChangeNode,
            NodeType.VariableAliasNode: VariableAliasNode,
        }

        return orm_to_pydantic[node.node_type]

    @staticmethod
    def get_type(val: Any) -> LiteralType:
        if isinstance(val, str):
            return LiteralType.String
        elif isinstance(val, int):
            return LiteralType.Integer
        elif isinstance(val, bool):
            return LiteralType.Boolean

    @staticmethod
    def cast_serialized(val: str, literal_type: LiteralType) -> Any:
        if literal_type is LiteralType.Integer:
            return int(val)
        elif literal_type is LiteralType.Boolean:
            return val == "True"
        return val

    """
    Writers
    """

    def data_asset_manager(self) -> DataAssetManager:
        pass

    def write_context(self, context: SessionContext) -> None:
        context_orm = SessionContextORM(**context.dict())

        self.session.add(context_orm)
        self.session.commit()

    def write_edges(self, edges: List[DirectedEdge]) -> None:
        for e in edges:
            self.write_single_edge(e)

    def write_nodes(self, nodes: List[Node]) -> None:
        for n in nodes:
            self.write_single_node(n)

    def write_single_edge(self, edge: DirectedEdge) -> None:
        edge_orm = DirectedEdgeORM(**edge.dict())

        self.session.add(edge_orm)
        self.session.commit()

    def write_single_node(self, node: Node) -> None:
        args = node.dict()
        if node.node_type is NodeType.ImportNode:
            del args["module"]
        elif node.node_type in [NodeType.CallNode, NodeType.StateChangeNode]:
            del args["value"]

        if node.node_type is NodeType.ArgumentNode:
            node = cast(ArgumentNode, node)
            if node.value_literal is not None:
                args["value_literal_type"] = LineaDB.get_type(node.value_literal)

        if node.node_type is NodeType.LiteralAssignNode:
            node = cast(LiteralAssignNode, node)
            args["value_type"] = LineaDB.get_type(node.value)

        node_orm = LineaDB.get_orm(node)(**args)

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

    def get_context(self, linea_id: LineaID) -> SessionContext:
        query_obj = (
            self.session.query(SessionContextORM)
            .filter(SessionContextORM.id == linea_id)
            .one()
        )
        return SessionContext.from_orm(query_obj)

    def get_node_by_id(self, linea_id: LineaID) -> Node:
        """
        Returns the node by looking up the database by ID
        """

        query_obj = self.session.query(NodeORM).filter(NodeORM.id == linea_id).one()
        obj = LineaDB.get_pydantic(query_obj).from_orm(query_obj)

        # cast string serialized values to their appropriate types
        if query_obj.node_type is NodeType.LiteralAssignNode:
            obj.value = LineaDB.cast_serialized(obj.value, query_obj.value_type)
        elif query_obj.node_type is NodeType.ArgumentNode:
            if obj.value_literal is not None:
                obj.value_literal = LineaDB.cast_serialized(
                    obj.value_literal, query_obj.value_literal_type
                )

        return obj

    def get_edge(self, source_node_id: LineaID, sink_node_id: LineaID) -> DirectedEdge:
        """
        Returns the directed edge by looking up the database by source and sink node IDs
        """

        query_obj = (
            self.session.query(DirectedEdgeORM)
            .filter(
                and_(
                    DirectedEdgeORM.source_node_id == source_node_id,
                    DirectedEdgeORM.sink_node_id == sink_node_id,
                )
            )
            .one()
        )
        return DirectedEdge.from_orm(query_obj)

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
