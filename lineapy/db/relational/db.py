from typing import Set, cast

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.expression import and_

from lineapy.data.graph import Graph
from lineapy.data.types import *
from lineapy.db.asset_manager.local import LocalDataAssetManager, DataAssetManager
from lineapy.db.base import LineaDBConfig, LineaDB
from lineapy.db.relational.schema.relational import *


class RelationalLineaDB(LineaDB):
    """
    - Note that LineaDB coordinates with assset manager and relational db.
      - The asset manager deals with binaries (e.g., cached values) - the relational db deals with more structured data,
      such as the Nodes and edges.
    - Also, at some point we might have a "cache" such that the readers don't have to go to the database if it's already
    ready, but that's lower priority.
    """

    def __init__(self):
        self.session: Optional[scoped_session] = None
        self._data_asset_manager: Optional[DataAssetManager] = None

    def init_db(self, config: LineaDBConfig):
        # TODO: we eventually need some configurations
        # create_engine params from
        # https://stackoverflow.com/questions/21766960/operationalerror-no-such-table-in-flask-with-sqlalchemy
        engine = create_engine(
            config.database_uri,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=True,
        )
        self.session = scoped_session(sessionmaker())
        self.session.configure(bind=engine)
        Base.metadata.create_all(engine)

        self._data_asset_manager = LocalDataAssetManager(self.session)

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
            NodeType.LoopNode: LoopNode,
            NodeType.DataSourceNode: DataSourceNode,
            NodeType.StateChangeNode: StateChangeNode,
            NodeType.VariableAliasNode: VariableAliasNode,
        }

        return orm_to_pydantic[node.node_type]

    @staticmethod
    def get_type(val: Any) -> LiteralType:
        def is_integer(val):
            try:
                int(val)
            except Exception as e:
                return False
            return True

        if isinstance(val, str):
            return LiteralType.String
        elif is_integer(val):
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

    @staticmethod
    def cast_dataset(val: Any) -> str:
        if hasattr(val, "to_csv"):
            return val.to_csv(index=False)
        return None

    """
    Writers
    """

    def data_asset_manager(self) -> DataAssetManager:
        return self._data_asset_manager

    def write_context(self, context: SessionContext) -> None:
        args = context.dict()

        for i in range(len(args["libraries"])):
            lib_args = context.libraries[i].dict()
            lib_args["session_id"] = context.id
            library_orm = LibraryORM(**lib_args)
            self.session.add(library_orm)

            args["libraries"][i] = library_orm

        context_orm = SessionContextORM(**args)

        self.session.add(context_orm)
        self.session.commit()

    def write_nodes(self, nodes: List[Node]) -> None:
        for n in nodes:
            self.write_single_node(n)

    def write_node_values(self, nodes: List[Node], version: int) -> None:
        for n in nodes:
            self.write_single_node_value(n, version)

    def write_single_node(self, node: Node) -> None:
        args = node.dict()
        if node.node_type is NodeType.ArgumentNode:
            node = cast(ArgumentNodeORM, node)
            args["value_literal_type"] = RelationalLineaDB.get_type(
                args["value_literal"]
            )

        elif node.node_type is NodeType.CallNode:
            node = cast(CallNodeORM, node)
            for arg in node.arguments:
                self.session.execute(
                    call_node_association_table.insert(),
                    params={"call_node_id": node.id, "argument_node_id": arg},
                )
            del args["arguments"]
            del args["value"]

        elif node.node_type in [
            NodeType.LoopNode,
            NodeType.ConditionNode,
            NodeType.FunctionDefinitionNode,
        ]:
            node = cast(SideEffectsNodeORM, node)

            if node.state_change_nodes is not None:
                for state_change_id in node.state_change_nodes:
                    self.session.execute(
                        side_effects_state_change_association_table.insert(),
                        params={
                            "side_effects_node_id": node.id,
                            "state_change_node_id": state_change_id,
                        },
                    )

            if node.import_nodes is not None:
                for import_id in node.import_nodes:
                    self.session.execute(
                        side_effects_import_association_table.insert(),
                        params={
                            "side_effects_node_id": node.id,
                            "import_node_id": import_id,
                        },
                    )

            if (
                node.node_type is NodeType.ConditionNode
                and node.dependent_variables_in_predicate is not None
            ):
                node = cast(ConditionNodeORM, node)
                for dependent_id in node.dependent_variables_in_predicate:
                    self.session.execute(
                        condition_association_table.insert(),
                        params={
                            "condition_node_id": node.id,
                            "dependent_node_id": dependent_id,
                        },
                    )
                del args["dependent_variables_in_predicate"]

            del args["state_change_nodes"]
            del args["import_nodes"]

        elif node.node_type is NodeType.ImportNode:
            node = cast(ImportNodeORM, node)
            args["library_id"] = node.library.id
            del args["library"]
            del args["module"]

        elif node.node_type is NodeType.StateChangeNode:
            del args["value"]

        elif node.node_type is NodeType.LiteralAssignNode:
            node = cast(LiteralAssignNodeORM, node)
            args["value_type"] = RelationalLineaDB.get_type(node.value)

        node_orm = RelationalLineaDB.get_orm(node)(**args)

        self.session.add(node_orm)
        self.session.commit()

        self.write_single_node_value(node, version=1)

    def write_single_node_value(self, node: Node, version: int) -> None:
        self.data_asset_manager().write_node_value(node, version)

    def add_node_id_to_artifact_table(
        self,
        node_id: LineaID,
        context_id: LineaID,
        name: str = "",
        date_created: str = "",
        code: LineaID = "",
        value_type: str = "",
    ) -> None:
        """
        Given that whether something is an artifact is just a human annotation, we are going to _exclude_ the information from the Graph Node types and just have a table that tracks what Node IDs are deemed as artifacts.
        """
        # - check node type: should just be CallNode and FunctionDefinitionNode
        #
        # - then insert into a table that's literally just the NodeID and maybe a timestamp for when it was registered as artifact

        node = self.get_node_by_id(node_id)
        if node.node_type in [NodeType.CallNode, NodeType.FunctionDefinitionNode]:
            artifact = ArtifactORM(
                id=node_id,
                context=context_id,
                value_type=value_type,
                name=name,
                date_created=date_created,
                code=code,
            )
            self.session.add(artifact)
            self.session.commit()

    def remove_node_id_from_artifact_table(self, node_id: LineaID) -> None:
        """
        The opposite of write_node_is_artifact
        - for now we can just delete it directly
        """
        self.session.query(ArtifactORM).filter(ArtifactORM.id == node_id).delete()
        self.session.commit()

    """
    Readers
    """

    def get_context(self, linea_id: LineaID) -> SessionContext:
        query_obj = (
            self.session.query(SessionContextORM)
            .filter(SessionContextORM.id == linea_id)
            .one()
        )
        obj = SessionContext.from_orm(query_obj)
        return obj

    def get_nodes_from_db(self) -> List[Node]:
        node_orms = self.session.query(NodeORM).all()
        nodes = []
        for orm in node_orms:
            nodes.append(self.get_node_by_id(orm.id))
        return nodes

    def get_node_by_id(self, linea_id: LineaID) -> Node:
        """
        Returns the node by looking up the database by ID
        """

        node = self.session.query(NodeORM).filter(NodeORM.id == linea_id).one()

        # cast string serialized values to their appropriate types
        if node.node_type is NodeType.LiteralAssignNode:
            node = cast(LiteralAssignNodeORM, node)
            node.value = RelationalLineaDB.cast_serialized(node.value, node.value_type)
        elif node.node_type is NodeType.ArgumentNode:
            node = cast(ArgumentNodeORM, node)
            if node.value_literal is not None:
                node.value_literal = RelationalLineaDB.cast_serialized(
                    node.value_literal, node.value_literal_type
                )
        elif node.node_type is NodeType.ImportNode:
            node = cast(ImportNodeORM, node)
            library_orm = (
                self.session.query(LibraryORM)
                .filter(LibraryORM.id == node.library_id)
                .one()
            )
            node.library = Library.from_orm(library_orm)
        elif node.node_type is NodeType.CallNode:
            node = cast(CallNodeORM, node)
            arguments = (
                self.session.query(call_node_association_table)
                .filter(call_node_association_table.c.call_node_id == node.id)
                .all()
            )
            node.arguments = [a.argument_node_id for a in arguments]

        # TODO: find a way to have this just check for SideEffectsNode type
        elif node.node_type in [
            NodeType.LoopNode,
            NodeType.ConditionNode,
            NodeType.FunctionDefinitionNode,
        ]:
            node = cast(SideEffectsNodeORM, node)
            state_change_nodes = (
                self.session.query(side_effects_state_change_association_table)
                .filter(
                    side_effects_state_change_association_table.c.side_effects_node_id
                    == node.id
                )
                .all()
            )

            if state_change_nodes is not None:
                node.state_change_nodes = [
                    a.state_change_node_id for a in state_change_nodes
                ]

            import_nodes = (
                self.session.query(side_effects_import_association_table)
                .filter(
                    side_effects_import_association_table.c.side_effects_node_id
                    == node.id
                )
                .all()
            )

            if import_nodes is not None:
                node.import_nodes = [a.import_node_id for a in import_nodes]

            if node.node_type is NodeType.ConditionNode:
                node = cast(ConditionNodeORM, node)
                dependent_variables_in_predicate = (
                    self.session.query(condition_association_table)
                    .filter(condition_association_table.c.condition_node_id == node.id)
                    .all()
                )

                if dependent_variables_in_predicate is not None:
                    node.dependent_variables_in_predicate = [
                        a.dependent_node_id for a in dependent_variables_in_predicate
                    ]

        return RelationalLineaDB.get_pydantic(node).from_orm(node)

    def get_node_value(self, node_id: LineaID, version: int) -> Optional[NodeValue]:
        value_orm = (
            self.session.query(NodeValueORM)
            .filter(
                and_(NodeValueORM.node_id == node_id, NodeValueORM.version == version)
            )
            .first()
        )
        if value_orm is not None:
            return value_orm.value
        return None

    def get_artifact(self, artifact_id: LineaID) -> Optional[Artifact]:
        return Artifact.from_orm(
            self.session.query(ArtifactORM)
            .filter(ArtifactORM.id == artifact_id)
            .first()
        )

    def jsonify_artifact(self, artifact: Artifact) -> Dict:
        json_artifact = artifact.dict()

        json_artifact["type"] = json_artifact["value_type"]
        del json_artifact["value_type"]

        json_artifact["date"] = json_artifact["date_created"]
        del json_artifact["date_created"]

        json_artifact["file"] = ""

        code = Code.from_orm(
            self.session.query(CodeORM).filter(CodeORM.id == artifact.code).first()
        )
        json_artifact["code"] = code.dict()

        token_associations = (
            self.session.query(code_token_association_table)
            .filter(code_token_association_table.c.code == code.id)
            .all()
        )
        # NOTE/TODO: currently only supports DataFrames and values as tokens
        tokens_json = []
        if token_associations is not None:
            for association in token_associations:
                token_orm = (
                    self.session.query(TokenORM)
                    .filter(TokenORM.id == association.token)
                    .first()
                )
                token_json = Token.from_orm(token_orm).dict()

                intermediate_value = (
                    self.session.query(NodeValueORM)
                    .filter(NodeValueORM.node_id == token_json["intermediate"])
                    .first()
                    .value
                )

                # check object type (for now this only supports DataFrames and values)
                intermediate_value = RelationalLineaDB.cast_dataset(intermediate_value)
                intermediate = {
                    "file": "",
                    "id": token_json["intermediate"],
                    "name": "",
                    "type": DATASET_TYPE,
                    "date": "1372944000",
                    "text": intermediate_value,
                }
                token_json["intermediate"] = intermediate
                tokens_json.append(token_json)

        json_artifact["code"]["tokens"] = tokens_json

        return json_artifact

    def get_graph_from_artifact_id(
        self, artifact_id: LineaID, session_context: LineaID
    ) -> Graph:
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
        nodes = self.get_nodes_from_db()
        full_graph = Graph(nodes)
        artifact = full_graph.get_node(artifact_id)
        ancestors = full_graph.get_ancestors(artifact)
        ancestors.append(artifact_id)
        return Graph([full_graph.get_node(a) for a in ancestors])
        # node_ids = list(self.get_ancestors_from_node(artifact_id))
        # node_ids.append(artifact_id)
        # nodes = [self.get_node_by_id(node_id) for node_id in node_ids]
        # return Graph(nodes)

    def get_ancestors_from_node(self, node_id: LineaID) -> Set[LineaID]:
        node = self.get_node_by_id(node_id)
        parents = Graph.get_parents_from_node(node)
        ancestors = set(parents)

        for parent in parents:
            new_ancestors = self.get_ancestors_from_node(parent)
            ancestors.update(new_ancestors)

        return ancestors

    def find_all_artifacts_derived_from_data_source(
        self, program: Graph, data_source_node: DataSourceNode
    ) -> List[Node]:
        descendants = program.get_descendants(data_source_node.id)
        artifacts = []
        for d_id in descendants:
            artifact = (
                self.session.query(ArtifactORM).filter(ArtifactORM.id == d_id).first()
            )
            if artifact is not None:
                artifacts.append(program.get_node(d_id))
        return artifacts

    def gather_artifact_intermediate_nodes(self, program: Graph):
        """
        While this is on a single graph, it actually requires talking to the data asset manager, so didn't get put into the MetadataExtractor.
        """
