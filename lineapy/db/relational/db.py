from typing import Set, Union, cast

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.expression import and_

from lineapy.data.graph import Graph
from lineapy.data.types import *
from lineapy.db.asset_manager.local import (
    LocalDataAssetManager,
    DataAssetManager,
)
from lineapy.db.db_utils import is_integer
from lineapy.db.base import LineaDBConfig, LineaDB
from lineapy.db.relational.schema.relational import *
from lineapy.utils import (
    CaseNotHandledError,
    EntryNotFoundError,
    NullValueError,
    info_log,
)

LineaIDAlias = Union[LineaID, LineaIDORM]


class RelationalLineaDB(LineaDB):
    """
    - Note that LineaDB coordinates with assset manager and relational db.
      - The asset manager deals with binaries (e.g., cached values) - the relational db deals with more structured data,
      such as the Nodes and edges.
    - Also, at some point we might have a "cache" such that the readers don't have to go to the database if it's already
    ready, but that's lower priority.
    """

    def __init__(self):
        self._data_asset_manager: Optional[DataAssetManager] = None

    @property
    def session(self) -> scoped_session:
        if self._session:
            return self._session
        raise NullValueError("db should have been initialized")

    @session.setter
    def session(self, value):
        self._session = value

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

        return pydantic_to_orm[node.node_type]  # type: ignore

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

        return orm_to_pydantic[node.node_type]  # type: ignore

    @staticmethod
    def get_type_of_literal_value(val: Any) -> LiteralType:

        if isinstance(val, str):
            return LiteralType.String
        elif is_integer(val):
            return LiteralType.Integer
        elif isinstance(val, bool):
            return LiteralType.Boolean
        raise CaseNotHandledError(f"Literal {val} is of type {type(val)}.")

    @staticmethod
    def cast_str_to_literal_value(val: str, literal_type: LiteralType) -> Any:
        if literal_type is LiteralType.Integer:
            return int(val)
        elif literal_type is LiteralType.Boolean:
            return val == "True"
        return val

    """
    Writers
    """

    @property
    def data_asset_manager(self) -> DataAssetManager:
        if self._data_asset_manager:
            return self._data_asset_manager
        raise NullValueError("data asset manager should have been initialized")

    @data_asset_manager.setter
    def data_asset_manager(self, value: DataAssetManager) -> None:
        self._data_asset_manager = value

    def write_context(self, context: SessionContext) -> None:
        args = context.dict()

        if context.libraries:
            for i in range(len(args["libraries"])):
                lib_args = context.libraries[i].dict()
                lib_args["session_id"] = context.id
                library_orm = LibraryORM(**lib_args)
                self.session.add(library_orm)

                args["libraries"][i] = library_orm
        else:
            args["libraries"] = []

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

        def set_value_type():
            v = args["value"]
            if v is not None:
                val_type = RelationalLineaDB.get_type_of_literal_value(v)
                args["value_type"] = val_type

        if (
            node.node_type is NodeType.ArgumentNode
            or node.node_type is NodeType.LiteralAssignNode
        ):
            set_value_type()

        elif node.node_type is NodeType.CallNode:
            node = cast(CallNode, node)
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
            node = cast(SideEffectsNode, node)

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

            if node.node_type is NodeType.ConditionNode:
                node = cast(ConditionNode, node)
                if node.dependent_variables_in_predicate is not None:

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
            node = cast(ImportNode, node)
            args["library_id"] = node.library.id
            del args["library"]
            del args["module"]

        elif node.node_type is NodeType.StateChangeNode:
            del args["value"]

        node_orm = RelationalLineaDB.get_orm(node)(**args)

        info_log("Writing node", node.id)
        self.session.add(node_orm)
        self.session.commit()

        self.write_single_node_value(node, version=1)

    def write_single_node_value(self, node: Node, version: int) -> None:
        self.data_asset_manager.write_node_value(node, version)

    def add_node_id_to_artifact_table(
        self,
        node_id: LineaID,
        date_created: float,
        description: Optional[str] = None,
    ) -> None:
        """
        Given that whether something is an artifact is just a human annotation, we are going to _exclude_ the information from the Graph Node types and just have a table that tracks what Node IDs are deemed as artifacts.
        """
        # - check node type: should just be CallNode and FunctionDefinitionNode
        #
        # - then insert into a table that's literally just the NodeID and maybe a timestamp for when it was registered as artifact
        # figure out DataAssetType
        # value_type,
        node = self.get_node_by_id(node_id)
        if node.node_type in [
            NodeType.CallNode,
            NodeType.FunctionDefinitionNode,
        ]:
            artifact = ArtifactORM(
                id=node_id,
                description=description,
                date_created=date_created,
            )
            self.session.add(artifact)
            self.session.commit()

    def remove_node_id_from_artifact_table(self, node_id: LineaIDAlias) -> None:
        """
        The opposite of write_node_is_artifact
        - for now we can just delete it directly
        """
        self.session.query(ArtifactORM).filter(
            ArtifactORM.id == node_id
        ).delete()
        self.session.commit()

    """
    Readers
    """

    def get_nodes_by_file_name(self, file_name: str):
        """
        First queries SessionContext for file_name
        Then find all the nodes by session_id
        Note:
        - This is currently used for testing purposes
        - TODO: finish enumerating over all the tables (just a subset for now)
        - FIXME: I wonder if there is a way to write this in a single query, I would refer for the database to optimize this instead of relying on the ORM.
        """
        session_context = (
            self.session.query(SessionContextORM)
            .filter(SessionContextORM.file_name == file_name)
            .one()
        )
        # enumerating over all the tables...
        call_nodes = (
            self.session.query(CallNodeORM)
            .filter(CallNodeORM.session_id == session_context.id)
            .all()
        )
        argument_nodes = (
            self.session.query(ArgumentNodeORM)
            .filter(ArgumentNodeORM.session_id == session_context.id)
            .all()
        )
        call_nodes.extend(argument_nodes)
        nodes = [self.map_orm_to_pydantic(node) for node in call_nodes]
        return nodes

    def get_context(self, linea_id: LineaIDAlias) -> SessionContext:
        query_obj = (
            self.session.query(SessionContextORM)
            .filter(SessionContextORM.id == linea_id)
            .one()
        )
        obj = SessionContext.from_orm(query_obj)
        return obj

    def get_node_by_id(self, linea_id: LineaIDAlias) -> Node:
        """
        Returns the node by looking up the database by ID
        SQLAlchemy is able to translate between the two types on demand
        """
        # linea_id_orm = LineaIDORM().process_bind_param(linea_id)
        try:
            node = (
                self.session.query(NodeORM).filter(NodeORM.id == linea_id).one()
            )
            return self.map_orm_to_pydantic(node)
        except:
            raise EntryNotFoundError(f"Did not find ID {linea_id}")

    def map_orm_to_pydantic(self, node: NodeORM) -> Node:
        # cast string serialized values to their appropriate types
        if node.node_type in [
            NodeType.LiteralAssignNode,
            NodeType.ArgumentNode,
        ]:
            if node.value is not None:
                node.value = RelationalLineaDB.cast_str_to_literal_value(
                    node.value, node.value_type
                )
        elif node.node_type is NodeType.ImportNode:
            node = cast(ImportNode, node)
            library_orm = (
                self.session.query(LibraryORM)
                .filter(LibraryORM.id == node.library_id)
                .one()
            )
            node.library = Library.from_orm(library_orm)
        elif node.node_type is NodeType.CallNode:
            node = cast(CallNode, node)
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
            node = cast(SideEffectsNode, node)
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
                node = cast(ConditionNode, node)
                dependent_variables_in_predicate = (
                    self.session.query(condition_association_table)
                    .filter(
                        condition_association_table.c.condition_node_id
                        == node.id
                    )
                    .all()
                )

                if dependent_variables_in_predicate is not None:
                    node.dependent_variables_in_predicate = [
                        a.dependent_node_id
                        for a in dependent_variables_in_predicate
                    ]

        return RelationalLineaDB.get_pydantic(node).from_orm(node)

    def get_latest_node_version(self, node_id: LineaIDAlias):
        """
        FIXME: this should be addressed by the new PR Dhruv is putting in
        """
        return self.session.query(func.max(NodeValueORM.version)).scalar()

    def get_node_value(
        self,
        node_id: LineaIDAlias,
        optional_version: Optional[int] = None,
    ) -> Optional[NodeValue]:
        """
        If the version is not provided, then fetch the latest version
        """
        version = (
            optional_version
            if optional_version
            else self.get_latest_node_version(node_id)
        )
        value_orm = (
            self.session.query(NodeValueORM)
            .filter(
                and_(
                    NodeValueORM.node_id == node_id,
                    NodeValueORM.version == version,
                )
            )
            .first()
        )
        return value_orm

    def get_artifact(self, artifact_id: LineaIDAlias) -> Optional[Artifact]:
        return Artifact.from_orm(
            self.session.query(ArtifactORM)
            .filter(ArtifactORM.id == artifact_id)
            .first()
        )

    def get_all_artifact_ids(self) -> List[LineaID]:
        artifact_orms = self.session.query(ArtifactORM).all()
        return [artifact.id for artifact in artifact_orms]

    def get_all_artifacts(self) -> List[Artifact]:
        artifact_orms = self.session.query(ArtifactORM).all()
        return [Artifact.from_orm(artifact) for artifact in artifact_orms]

    def get_graph_from_artifact_id(self, artifact_id: LineaIDAlias) -> Graph:
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
        node_ids = list(self.get_ancestors_from_node(artifact_id))
        node_ids.append(artifact_id)
        nodes = [self.get_node_by_id(node_id) for node_id in node_ids]
        return Graph(nodes)

    def get_ancestors_from_node(
        self, node_id: LineaIDAlias
    ) -> Set[LineaIDAlias]:
        node = self.get_node_by_id(node_id)
        parents = Graph.get_parents_from_node(node)
        ancestors = set(parents)

        for parent in parents:
            new_ancestors = self.get_ancestors_from_node(parent)
            ancestors.update(new_ancestors)

        return ancestors

    def find_all_artifacts_derived_from_data_source(
        self,
        program: Graph,
        data_source_node: DataSourceNode,
    ) -> List[Node]:
        """
        FIXME: need to search through all graphs, not just the graph passed in
        TODO: this seems inefficient?
        """
        descendants = program.get_descendants(data_source_node.id)
        artifacts = []
        for d_id in descendants:
            artifact = (
                self.session.query(ArtifactORM)
                .filter(ArtifactORM.id == d_id)
                .first()
            )
            if artifact is not None:
                node = program.get_node(d_id)
                if node is not None:
                    artifacts.append(node)
        return artifacts

    def gather_artifact_call_nodes(self, program: Graph):
        """
        This gathers:
        - the code (TODO, in Dhruv's other PR)
        - the ancestor call nodes
        """
        # I will do this after merging with master
        pass
