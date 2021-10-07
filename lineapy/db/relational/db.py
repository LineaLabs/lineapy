import logging
import os
from pathlib import Path
from typing import List, Optional, cast, Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.expression import and_

from lineapy.constants import SQLALCHEMY_ECHO
from lineapy.data.graph import Graph
from lineapy.data.types import (
    ArgumentNode,
    Artifact,
    JupyterCell,
    Library,
    LineaID,
    LookupNode,
    NodeValue,
    SessionContext,
    CallNode,
    ImportNode,
    LiteralNode,
    DataSourceNode,
    SourceCode,
    SourceLocation,
    StateChangeNode,
    VariableNode,
    Node,
)
from lineapy.db.asset_manager.local import (
    LocalDataAssetManager,
    DataAssetManager,
)
from lineapy.db.base import LineaDBConfig, LineaDB
from lineapy.db.relational.schema.relational import *
from lineapy.graph_reader.program_slice import get_program_slice
from lineapy.utils import (
    CaseNotHandledError,
    NullValueError,
    is_integer,
    get_literal_value_from_string,
)


class RelationalLineaDB(LineaDB):
    """
    - Note that LineaDB coordinates with assset manager and relational db.
      - The asset manager deals with binaries (e.g., cached values)
        The relational db deals with more structured data,
        such as the Nodes and edges.
    - Also, at some point we might have a "cache" such that the readers
        don't have to go to the database if it's already
        loaded, but that's low priority.
    """

    def __init__(self):
        self._data_asset_manager: Optional[DataAssetManager] = None
        self._session: Optional[scoped_session] = None

    @property
    def session(self) -> scoped_session:
        if self._session is not None:
            return self._session
        raise NullValueError("db should have been initialized")

    @session.setter
    def session(self, value):
        self._session = value

    def init_db(self, config: LineaDBConfig):
        # TODO: we eventually need some configurations
        # create_engine params from
        # https://stackoverflow.com/questions/21766960/operationalerror-no-such-table-in-flask-with-sqlalchemy
        echo = os.getenv(SQLALCHEMY_ECHO, default=False)
        if not isinstance(echo, bool):
            echo = (
                str.lower(os.getenv(SQLALCHEMY_ECHO, default=True)) == "true"
            )
        logging.info(f"Starting DB at {config.database_uri}")
        engine = create_engine(
            config.database_uri,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=echo,
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
            NodeType.LiteralNode: LiteralNodeORM,
            NodeType.DataSourceNode: DataSourceNodeORM,
            NodeType.StateChangeNode: StateChangeNodeORM,
            NodeType.VariableNode: VariableNodeORM,
            NodeType.LookupNode: LookupNodeORM,
        }

        return pydantic_to_orm[node.node_type]  # type: ignore

    @staticmethod
    def get_pydantic(node: NodeORM) -> Node:
        orm_to_pydantic = {
            NodeType.ArgumentNode: ArgumentNode,
            NodeType.CallNode: CallNode,
            NodeType.ImportNode: ImportNode,
            NodeType.LiteralNode: LiteralNode,
            NodeType.DataSourceNode: DataSourceNode,
            NodeType.StateChangeNode: StateChangeNode,
            NodeType.VariableNode: VariableNode,
            NodeType.LookupNode: LookupNode,
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

    def write_library(
        self, library: Library, context_id: LineaID
    ) -> LibraryORM:
        lib_args = library.dict()
        lib_args["session_id"] = context_id
        library_orm = LibraryORM(**lib_args)
        self.session.add(library_orm)
        return library_orm

    def write_context(self, context: SessionContext) -> None:
        args = context.dict()

        context_orm = SessionContextORM(**args)

        self.session.add(context_orm)
        self.session.commit()

    def write_source_code(self, source_code: SourceCode) -> None:
        """
        Writes a source code object to the database.

        It first has to convert it to a SourceCodeORM object, which has the fields
        inlined instead of a union
        """
        source_code_orm = SourceCodeORM(
            id=source_code.id, code=source_code.code
        )
        location = source_code.location
        if isinstance(location, Path):
            source_code_orm.path = str(location)
            source_code_orm.jupyter_execution_count = None
            source_code_orm.jupyter_session_id = None
        else:
            source_code_orm.path = None
            source_code_orm.jupyter_execution_count = location.execution_count
            source_code_orm.jupyter_session_id = location.session_id

        self.session.add(source_code_orm)
        self.session.commit()

    def add_lib_to_session_context(
        self, context_id: LineaID, library: Library
    ):
        library_orm = self.write_library(library, context_id)
        self.session.commit()

    def write_nodes(self, nodes: List[Node]) -> None:
        for n in nodes:
            self.write_single_node(n)
        self.write_node_values(nodes)

    def write_single_node(self, node: Node) -> None:
        args = node.dict(exclude={"source_location"})
        # Map source location sub model in memory node, to inlined attributes
        # in ORM and map source code to foreign key
        source_location = node.source_location
        if source_location is not None:
            args["lineno"] = source_location.lineno
            args["col_offset"] = source_location.col_offset
            args["end_lineno"] = source_location.end_lineno
            args["end_col_offset"] = source_location.end_col_offset
            args["source_code_id"] = source_location.source_code.id
        else:
            args["lineno"] = None
            args["col_offset"] = None
            args["end_lineno"] = None
            args["end_col_offset"] = None
            args["source_code_id"] = None

        if node.node_type is NodeType.CallNode:
            node = cast(CallNodeORM, node)
            for arg in node.arguments:
                self.session.execute(
                    call_node_association_table.insert(),
                    params={"call_node_id": node.id, "argument_node_id": arg},
                )
            del args["arguments"]
            del args["value"]

        elif node.node_type is NodeType.ImportNode:
            node = cast(ImportNodeORM, node)
            args["library_id"] = node.library.id
            del args["library"]
            del args["value"]

        elif node.node_type is NodeType.StateChangeNode:
            del args["value"]

        elif node.node_type is NodeType.LiteralNode:
            node = cast(LiteralNodeORM, node)
            if node.value is not None:
                args[
                    "value_type"
                ] = RelationalLineaDB.get_type_of_literal_value(node.value)

        elif node.node_type is NodeType.LookupNode:
            del args["value"]

        elif node.node_type is NodeType.VariableNode:
            """
            The value is just for run time information
            """
            del args["value"]

        node_orm = RelationalLineaDB.get_orm(node)(**args)

        self.session.add(node_orm)
        self.session.commit()

    def write_node_values(
        self,
        nodes: List[Node],
        version: Optional[int] = None,
    ) -> None:
        # Lookup version if we don't know
        if version is None:
            # TODO: look up
            version = 1  # eff it...
        for n in nodes:
            graph_cache_veto = False
            if isinstance(n, CallNode):
                # look up the function_id
                fun_node = next(x for x in nodes if x.id == n.function_id)
                if isinstance(fun_node, LookupNode):
                    if fun_node.name == "__exec__":
                        graph_cache_veto = True
            else:
                graph_cache_veto = True
            self.write_single_node_value(n, version, graph_cache_veto)

    def write_single_node_value(
        self, node: Node, version: int, graph_cache_veto: bool
    ) -> None:
        self.data_asset_manager.write_node_value(
            node, version, graph_cache_veto
        )

    def add_node_id_to_artifact_table(
        self,
        node_id: LineaID,
        date_created: float,
        name: Optional[str] = None,
        execution_time: Optional[float] = None,
    ) -> None:
        """
        Given that whether something is an artifact is just a human annotation,
        we are going to _exclude_ the information from the Graph Node types and
        just have a table that tracks what Node IDs are deemed as artifacts.
        """

        artifact = ArtifactORM(
            id=node_id,
            name=name,
            date_created=date_created,
        )
        self.session.add(artifact)

        # Currently each execution maps to exactly one artifact,
        # so for now we add a new execution every time we publish an artifact
        execution = ExecutionORM(
            artifact_id=artifact.id,
            version=1,
            execution_time=execution_time,
        )
        self.session.add(execution)
        self.session.commit()

    def remove_node_id_from_artifact_table(self, node_id: LineaID) -> None:
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

    def get_context(self, linea_id: str) -> SessionContext:
        query_obj = (
            self.session.query(SessionContextORM)
            .filter(SessionContextORM.id == linea_id)
            .one()
        )
        obj = SessionContext.from_orm(query_obj)
        return obj

    def get_node_by_id(self, linea_id: LineaID) -> Node:
        """
        Returns the node by looking up the database by ID
        SQLAlchemy is able to translate between the two types on demand
        """
        node = self.session.query(NodeORM).filter(NodeORM.id == linea_id).one()
        return self.map_orm_to_pydantic(node)

    def map_orm_to_pydantic(self, node: NodeORM) -> Node:
        # If we have source locations, save those on the node.
        if node.source_code_id != None:
            node.source_code.location = (  # type: ignore
                Path(node.source_code.path)
                if node.source_code.path
                else JupyterCell(
                    execution_count=node.source_code.jupyter_execution_count,
                    session_id=node.source_code.jupyter_session_id,
                )
            )
            # Call from_orm on itself, because it contains all the line number
            # calls on the ORM
            node.source_location = SourceLocation.from_orm(node)  # type: ignore

        # cast string serialized values to their appropriate types
        if node.node_type is NodeType.LiteralNode:
            node = cast(LiteralNodeORM, node)
            node.value = get_literal_value_from_string(
                node.value, node.value_type
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

        return RelationalLineaDB.get_pydantic(node).from_orm(node)

    def get_node_value_from_db(
        self, node_id: LineaID, version: int
    ) -> Optional[NodeValue]:
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

    def get_artifact(self, artifact_id: LineaID) -> Optional[Artifact]:
        return Artifact.from_orm(
            self.session.query(ArtifactORM)
            .filter(ArtifactORM.id == artifact_id)
            .first()
        )

    def get_artifact_by_name(self, artifact_name: str) -> ArtifactORM:
        """
        Gets a code slice for an artifact by name, assuming there is only
        one artifact with that name,
        """
        return (
            self.session.query(ArtifactORM)
            .filter(ArtifactORM.name == artifact_name)
            .one()
        )

    def get_all_artifacts(self) -> List[Artifact]:
        results = self.session.query(ArtifactORM).all()
        return [Artifact.from_orm(r) for r in results]

    def get_nodes_for_session(self, session_id: LineaID) -> List[Node]:
        """
        Get all the nodes associated with the session, which does
         NOT include things like SessionContext
        """
        node_orms = (
            self.session.query(NodeORM)
            .filter(NodeORM.session_id == session_id)
            .all()
        )
        return [self.map_orm_to_pydantic(node) for node in node_orms]

    # def get_session_graph_from_artifact_id(
    #     self, artifact_id: LineaID
    # ) -> Graph:
    #     """ """
    def get_all_nodes(self) -> List[Node]:
        node_orms = self.session.query(NodeORM).all()
        return [self.map_orm_to_pydantic(node) for node in node_orms]

    def get_session_graph_from_artifact_id(
        self, artifact_id: LineaID
    ) -> Graph:
        """
        - This is program slicing over database data.
        - There are lots of complexities when it comes to mutation
          - Examples:
            - Third party libraries have functions that mutate some global or
              variable state.
          - Strategy for now
            - definitely take care of the simple cases, like `VariableNode`
            - simple heuristics that may create false positives
              (include things not necessary)
            - but definitely NOT false negatives (then the program
              CANNOT be executed)
        """
        node = self.get_node_by_id(artifact_id)
        nodes = self.get_nodes_for_session(node.session_id)
        return Graph(nodes, self.get_context(node.session_id))

    def get_code_from_artifact_id(self, artifact_id: LineaID) -> str:
        """
        Get all the code associated with an artifact by retrieving the Graph
        associated with the artifact from the database and piecing together the
        code from the nodes. Note: The code is the program slice for the
        artifact, not all code associated with the session in which the
        artifact was generated.

        :param artifact_id: UUID for the artifact
        :return: string containing the code for generating the artifact.
        """
        graph = self.get_session_graph_from_artifact_id(artifact_id)
        return get_program_slice(graph, [artifact_id])

    def get_code_from_artifact_name(self, artifact_name: str) -> str:
        """
        Get all the code associated with an artifact by retrieving the Graph
        associated with the artifact from the database and piecing together the
        code from the nodes. Note: The code is the program slice for the
        artifact, not all code associated with the session in which the
        artifact was generated.

        :param artifact_name: Name of the artifact
        :return: string containing the code for generating the artifact.
        """
        artifacts = self.find_artifact_by_name(artifact_name)
        assert (
            len(artifacts) == 1
        ), "Should only be one artifact with this name"
        return self.get_code_from_artifact_id(artifacts[0].id)

    def find_all_artifacts_derived_from_data_source(
        self, program: Graph, data_source_node: DataSourceNode
    ) -> List[Node]:
        """
        Gets all of the artifacts contained in the input program graph that are
        descendents of data_source_node.

        :param program: a Graph object representing the program
        :param data_source_node: a node in program
        :return: nodes in program that are descendents of data_source_node.
        """
        descendants = program.get_descendants(data_source_node)
        artifacts = []
        for d_id in descendants:
            descendant_is_artifact = (
                self.session.query(ArtifactORM)
                .filter(ArtifactORM.id == d_id)
                .first()
            ) is not None
            descendant = program.get_node(d_id)
            if descendant_is_artifact and descendant is not None:
                artifacts.append(descendant)
        return artifacts

    def find_artifact_by_name(self, artifact_name: str) -> List[Artifact]:
        """
        Find artifacts from the database with `artifact_name` as specified by
        the user via `linea_publish`. Note: multiple artifacts can have the
        same name, hence the result can be a list instead of a single artifact.

        :param artifact_name: string containing the name of the artifact
        given by the user via `linea_publish`
        :return: a list of Artifact objects with artifact_name as its name.
        """
        query_result = (
            self.session.query(ArtifactORM)
            .filter(ArtifactORM.name == artifact_name)
            .all()
        )
        return [Artifact.from_orm(query_row) for query_row in query_result]
