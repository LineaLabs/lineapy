import logging
import os
from pathlib import Path
from typing import Any, List, Optional, cast

from sqlalchemy import create_engine
from sqlalchemy.orm import defaultload, scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.expression import and_

from lineapy.constants import SQLALCHEMY_ECHO, ExecutionMode
from lineapy.data.types import (
    Artifact,
    CallNode,
    Execution,
    GlobalNode,
    ImportNode,
    JupyterCell,
    Library,
    LineaID,
    LiteralNode,
    LiteralType,
    LookupNode,
    MutateNode,
    Node,
    NodeValue,
    SessionContext,
    SourceCode,
    SourceLocation,
)
from lineapy.db.base import LineaDBConfig, get_default_config_by_environment
from lineapy.db.relational.schema.relational import (
    ArtifactORM,
    Base,
    BaseNodeORM,
    CallNodeORM,
    ExecutionORM,
    GlobalNodeORM,
    GlobalReferenceORM,
    ImplicitDependencyORM,
    ImportNodeORM,
    KeywordArgORM,
    LibraryORM,
    LiteralNodeORM,
    LookupNodeORM,
    MutateNodeORM,
    NodeORM,
    NodeValueORM,
    PositionalArgORM,
    SessionContextORM,
    SourceCodeORM,
)
from lineapy.utils import get_literal_value_from_string

logger = logging.getLogger(__name__)


class RelationalLineaDB:
    """
    - Note that LineaDB coordinates with assset manager and relational db.
      - The asset manager deals with binaries (e.g., cached values)
        The relational db deals with more structured data,
        such as the Nodes and edges.
    - Also, at some point we might have a "cache" such that the readers
        don't have to go to the database if it's already
        loaded, but that's low priority.
    """

    @classmethod
    def from_environment(cls, mode: ExecutionMode) -> "RelationalLineaDB":
        """
        Creates a new database connection from the environment variables.
        """
        config = get_default_config_by_environment(mode)
        return cls(config)

    def __init__(self, config: LineaDBConfig):
        # TODO: we eventually need some configurations
        # create_engine params from
        # https://stackoverflow.com/questions/21766960/operationalerror-no-such-table-in-flask-with-sqlalchemy
        echo = os.getenv(SQLALCHEMY_ECHO, default="false").lower() == "true"
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

    @staticmethod
    def get_type_of_literal_value(val: Any) -> LiteralType:
        if isinstance(val, str):
            return LiteralType.String
        elif isinstance(val, bool):
            return LiteralType.Boolean
        elif isinstance(val, int):
            return LiteralType.Integer
        elif isinstance(val, float):
            return LiteralType.Float
        elif val is None:
            return LiteralType.NoneType
        raise NotImplementedError(f"Literal {val} is of type {type(val)}.")

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

    def commit(self) -> None:
        """
        End the transaction and commit the changes.
        """
        self.session.commit()

    def close(self):
        """
        Close the database connection.
        """
        # Always close, even if error is raised
        # https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.sessionmaker
        try:
            self.commit()
        finally:
            self.session.close()

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

    def add_lib_to_session_context(
        self, context_id: LineaID, library: Library
    ):
        self.write_library(library, context_id)

    def write_node(self, node: Node) -> None:
        args = node.dict(include={"id", "session_id", "node_type"})
        s = node.source_location
        if s:
            args["lineno"] = s.lineno
            args["col_offset"] = s.col_offset
            args["end_lineno"] = s.end_lineno
            args["end_col_offset"] = s.end_col_offset
            args["source_code_id"] = s.source_code.id

        node_orm: NodeORM
        if isinstance(node, CallNode):
            node_orm = CallNodeORM(
                **args,
                function_id=node.function_id,
                positional_args={
                    PositionalArgORM(index=i, arg_node_id=v)
                    for i, v in enumerate(node.positional_args)
                },
                keyword_args={
                    KeywordArgORM(name=k, arg_node_id=v)
                    for k, v in node.keyword_args.items()
                },
                global_reads={
                    GlobalReferenceORM(
                        call_node_id=node.id,
                        variable_name=k,
                        variable_node_id=id_,
                    )
                    for k, id_ in node.global_reads.items()
                },
                implicit_dependencies={
                    ImplicitDependencyORM(index=k, arg_node_id=id_)
                    for k, id_ in enumerate(node.implicit_dependencies)
                },
            )
        elif isinstance(node, ImportNode):
            node_orm = ImportNodeORM(
                **args,
                library_id=node.library.id,
            )

        elif isinstance(node, LiteralNode):
            # Not sure why we are passing in value ot the literal node,
            # since it isnt a field in the ORM?
            # We were previously so I kept it, confused by this!
            node_orm = LiteralNodeORM(  # type: ignore
                **args,
                value_type=RelationalLineaDB.get_type_of_literal_value(
                    node.value
                ),
                value=str(node.value),
            )
        elif isinstance(node, MutateNode):
            node_orm = MutateNodeORM(
                **args,
                call_id=node.call_id,
                source_id=node.source_id,
            )
        elif isinstance(node, GlobalNode):
            node_orm = GlobalNodeORM(
                **args, call_id=node.call_id, name=node.name
            )
        else:
            node_orm = LookupNodeORM(**args, name=node.name)

        self.session.add(node_orm)

    def write_node_value(
        self,
        node_value: NodeValue,
    ) -> None:
        self.session.add(NodeValueORM(**node_value.dict()))

    def write_artifact(self, artifact: Artifact) -> None:

        artifact_orm = ArtifactORM(
            id=artifact.id,
            name=artifact.name,
            date_created=artifact.date_created,
        )
        self.session.add(artifact_orm)

    def write_execution(self, execution: Execution) -> None:

        execution_orm = ExecutionORM(
            id=execution.id,
            timestamp=execution.timestamp,
        )
        self.session.add(execution_orm)

    """
    Readers
    """

    def map_orm_to_pydantic(self, node: NodeORM) -> Node:
        args: dict[str, Any] = {
            "id": node.id,
            "session_id": node.session_id,
            "node_type": node.node_type,
        }
        if node.source_code:
            source_code = SourceCode(
                id=node.source_code_id,
                code=node.source_code.code,
                location=(
                    Path(node.source_code.path)
                    if node.source_code.path
                    else JupyterCell(
                        execution_count=node.source_code.jupyter_execution_count,
                        session_id=node.source_code.jupyter_session_id,
                    )
                ),
            )
            args["source_location"] = SourceLocation(
                lineno=node.lineno,
                col_offset=node.col_offset,
                end_lineno=node.end_lineno,
                end_col_offset=node.end_col_offset,
                source_code=source_code,
            )
        # cast string serialized values to their appropriate types
        if isinstance(node, LiteralNodeORM):
            return LiteralNode(
                value=get_literal_value_from_string(
                    node.value, node.value_type
                ),
                **args,
            )
        if isinstance(node, ImportNodeORM):
            library_orm = (
                self.session.query(LibraryORM)
                .filter(LibraryORM.id == node.library_id)
                .one()
            )
            return ImportNode(library=Library.from_orm(library_orm), **args)
        if isinstance(node, CallNodeORM):
            positional_args = [
                v
                for _, v in sorted(
                    (
                        # Not sure why we need cast here, index field isn't optional
                        # but mypy thinks it is
                        (cast(int, p.index), p.arg_node_id)
                        for p in node.positional_args
                    ),
                    key=lambda p: p[0],
                )
            ]
            keyword_args = {n.name: n.arg_node_id for n in node.keyword_args}
            global_reads = {
                gr.variable_name: gr.variable_node_id
                for gr in node.global_reads
            }
            implicit_dependencies = [n for n in node.implicit_dependencies]
            return CallNode(
                function_id=node.function_id,
                positional_args=positional_args,
                keyword_args=keyword_args,
                global_reads=global_reads,
                implicit_dependencies=implicit_dependencies,
                **args,
            )
        if isinstance(node, MutateNodeORM):
            return MutateNode(
                call_id=node.call_id,
                source_id=node.source_id,
                **args,
            )
        if isinstance(node, GlobalNodeORM):
            return GlobalNode(
                call_id=node.call_id,
                name=node.name,
                **args,
            )
        return LookupNode(name=node.name, **args)

    def get_node_by_id(self, linea_id: LineaID) -> Node:
        """
        Returns the node by looking up the database by ID
        SQLAlchemy is able to translate between the two types on demand
        """
        node = (
            self.session.query(BaseNodeORM)
            .filter(BaseNodeORM.id == linea_id)
            .one()
        )
        return self.map_orm_to_pydantic(node)

    def get_session_context(self, linea_id: LineaID) -> SessionContext:
        query_obj = (
            self.session.query(SessionContextORM)
            .filter(SessionContextORM.id == linea_id)
            .one()
        )
        obj = SessionContext.from_orm(query_obj)
        return obj

    def get_node_value_from_db(
        self, node_id: LineaID, execution_id: LineaID
    ) -> Optional[NodeValueORM]:
        value_orm = (
            self.session.query(NodeValueORM)
            .filter(
                and_(
                    NodeValueORM.node_id == node_id,
                    NodeValueORM.execution_id == execution_id,
                )
            )
            .first()
        )
        return value_orm

    def get_artifacts_for_session(
        self, session_id: LineaID
    ) -> list[ArtifactORM]:
        """
        Gets a code slice for an artifact by name, assuming there is only
        one artifact with that name,
        """
        return (
            self.session.query(ArtifactORM)
            .filter(BaseNodeORM.session_id == session_id)
            # Don't include source code in query, since it's not needed
            .options(
                defaultload(ArtifactORM.node).raiseload(
                    BaseNodeORM.source_code
                )
            )
            .all()
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
        """
        Used by the catalog to get all the artifacts
        """
        results = self.session.query(ArtifactORM).all()
        return [Artifact.from_orm(r) for r in results]

    def get_nodes_for_session(self, session_id: LineaID) -> List[Node]:
        """
        Get all the nodes associated with the session, which does
         NOT include things like SessionContext
        """
        node_orms = (
            self.session.query(BaseNodeORM)
            .filter(BaseNodeORM.session_id == session_id)
            .all()
        )
        return [self.map_orm_to_pydantic(node) for node in node_orms]
