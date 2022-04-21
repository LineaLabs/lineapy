from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from sqlalchemy import create_engine
from sqlalchemy.orm import defaultload, scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.expression import and_

from lineapy.data.types import (
    Artifact,
    CallNode,
    Execution,
    GlobalNode,
    ImportNode,
    JupyterCell,
    KeywordArgument,
    LineaID,
    LiteralNode,
    LiteralType,
    LookupNode,
    MutateNode,
    Node,
    NodeValue,
    PositionalArgument,
    SessionContext,
    SourceCode,
    SourceLocation,
)
from lineapy.db.relational import (
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
    LiteralNodeORM,
    LookupNodeORM,
    MutateNodeORM,
    NodeORM,
    NodeValueORM,
    PositionalArgORM,
    SessionContextORM,
    SourceCodeORM,
)
from lineapy.db.utils import OVERRIDE_HELP_TEXT, resolve_db_url
from lineapy.exceptions.db_exceptions import ArtifactSaveException
from lineapy.exceptions.user_exception import UserException
from lineapy.utils.analytics.event_schemas import ExceptionEvent
from lineapy.utils.analytics.usage_tracking import track  # circular dep issues
from lineapy.utils.constants import DB_SQLITE_PREFIX, SQLALCHEMY_ECHO
from lineapy.utils.utils import get_literal_value_from_string

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

    def __init__(self, url: str):
        """
        Create a linea DB, by connecting to a database url:
        https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls
        """
        # create_engine params from
        # https://stackoverflow.com/questions/21766960/operationalerror-no-such-table-in-flask-with-sqlalchemy
        self.url: str = url
        echo = os.getenv(SQLALCHEMY_ECHO, default="false").lower() == "true"
        logger.debug(f"Connecting to Linea DB at {url}")
        additional_args = {}
        if url.startswith(DB_SQLITE_PREFIX):
            additional_args = {"check_same_thread": False}
        self.engine = create_engine(
            url,
            connect_args=additional_args,
            poolclass=StaticPool,
            echo=echo,
        )
        self.session = scoped_session(sessionmaker())
        self.session.configure(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def renew_session(self):
        if self.url.startswith(DB_SQLITE_PREFIX):
            self.commit()
            self.session = scoped_session(sessionmaker())
            self.session.configure(bind=self.engine)

    @classmethod
    def from_environment(cls, url: Optional[str] = None) -> RelationalLineaDB:
        f"""
        Creates a new database.

        url: {OVERRIDE_HELP_TEXT}
        """
        return cls(resolve_db_url(url))

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
        elif val is ...:
            return LiteralType.Ellipsis
        raise NotImplementedError(f"Literal {val} is of type {type(val)}.")

    def write_context(self, context: SessionContext) -> None:
        args = context.dict()

        context_orm = SessionContextORM(**args)

        self.session.add(context_orm)
        if not self.url.startswith(DB_SQLITE_PREFIX):
            self.session.flush()
        self.renew_session()

    def commit(self) -> None:
        """
        End the transaction and commit the changes.
        """
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise ArtifactSaveException() from e

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
        self.renew_session()

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
                    PositionalArgORM(
                        index=i, starred=v.starred, arg_node_id=v.id
                    )
                    for i, v in enumerate(node.positional_args)
                },
                keyword_args={
                    KeywordArgORM(
                        name=v.key, arg_node_id=v.value, starred=v.starred
                    )
                    for v in node.keyword_args
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
                name=node.name,
                version=node.version,
                package_name=node.package_name,
                path=node.path,
            )

        elif isinstance(node, LiteralNode):
            # The value_type is not currently used anywhere
            # Was used before for rendering to a web UI.
            # Keeping it for now for anticipation of platform work.
            node_orm = LiteralNodeORM(
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
        self.renew_session()

    def write_node_value(
        self,
        node_value: NodeValue,
    ) -> None:
        self.session.add(NodeValueORM(**node_value.dict()))
        self.renew_session()

    def write_artifact(self, artifact: Artifact) -> None:
        artifact_orm = ArtifactORM(
            node_id=artifact.node_id,
            execution_id=artifact.execution_id,
            name=artifact.name,
            date_created=artifact.date_created,
            version=artifact.version,
        )
        self.session.add(artifact_orm)
        self.renew_session()

    def artifact_in_db(
        self, node_id: LineaID, execution_id: LineaID, name: str, version: str
    ) -> bool:
        """
        Returns true if the artifact is already in the DB.
        """
        return self.session.query(
            self.session.query(ArtifactORM)
            .filter(
                and_(
                    ArtifactORM.node_id == node_id,
                    ArtifactORM.execution_id == execution_id,
                    ArtifactORM.name == name,
                    ArtifactORM.version == version,
                )
            )
            .exists()
        ).scalar()

    def write_execution(self, execution: Execution) -> None:

        execution_orm = ExecutionORM(
            id=execution.id,
            timestamp=execution.timestamp,
        )
        self.session.add(execution_orm)
        if not self.url.startswith(DB_SQLITE_PREFIX):
            self.session.flush()
        self.renew_session()

    """
    Readers
    """

    def map_orm_to_pydantic(self, node: NodeORM) -> Node:
        args: Dict[str, Any] = {
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
            return ImportNode(
                name=node.name,
                version=node.version,
                package_name=node.package_name,
                path=node.path,
                **args,
            )
        if isinstance(node, CallNodeORM):
            positional_args = [
                v
                for _, v in sorted(
                    (
                        # Not sure why we need cast here, index field isn't optional
                        # but mypy thinks it is
                        (
                            cast(int, p.index),
                            PositionalArgument(
                                id=p.arg_node_id, starred=p.starred
                            ),
                        )
                        for p in node.positional_args
                    ),
                    key=lambda p: p[0],
                )
            ]
            keyword_args = [
                KeywordArgument(
                    key=n.name, value=n.arg_node_id, starred=n.starred
                )
                for n in node.keyword_args
            ]
            global_reads = {
                gr.variable_name: gr.variable_node_id
                for gr in node.global_reads
            }
            implicit_dependencies = [
                n.arg_node_id for n in node.implicit_dependencies
            ]
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

    def node_value_in_db(
        self, node_id: LineaID, execution_id: LineaID
    ) -> bool:
        """
        Returns true if the node value is already in the DB.
        """
        return self.session.query(
            self.session.query(NodeValueORM)
            .filter(
                and_(
                    NodeValueORM.node_id == node_id,
                    NodeValueORM.execution_id == execution_id,
                )
            )
            .exists()
        ).scalar()

    def get_libraries_for_session(
        self, session_id: LineaID
    ) -> List[ImportNodeORM]:
        """
        Gets all dependencies for a session, assuming all the libs in a
        particular session will be required to set up a new env.

        TODO: I think this distinct is still broken, because we want to
        make it distinct on a subset of columns: session_id, name, and version.
        """
        return (
            self.session.query(ImportNodeORM)
            .filter(ImportNodeORM.session_id == session_id)
            .distinct()
            .all()
        )

    def get_artifacts_for_session(
        self, session_id: LineaID
    ) -> List[ArtifactORM]:
        """
        Gets a code slice for an artifact by name, assuming there is only
        one artifact with that name,
        """
        return (
            self.session.query(ArtifactORM)
            .filter(BaseNodeORM.session_id == session_id)
            .join(BaseNodeORM)
            # Don't include source code in query, since it's not needed
            .options(
                defaultload(ArtifactORM.node).raiseload(
                    BaseNodeORM.source_code
                )
            )
            .all()
        )

    def get_artifact_by_name(
        self, artifact_name: str, version: Optional[str] = None
    ) -> ArtifactORM:
        """
        Gets the most recent artifact with a certain name.
        If a version is not specified, it will return the most recent
        version sorted by date_created
        """
        res_query = self.session.query(ArtifactORM).filter(
            ArtifactORM.name == artifact_name
        )
        if version:
            res_query = res_query.filter(ArtifactORM.version == version)
        res = res_query.order_by(ArtifactORM.date_created.desc()).first()
        if res is None:
            msg = (
                f"Artifact {artifact_name} (version {version})"
                if version
                else f"Artifact {artifact_name}"
            )
            track(ExceptionEvent("UserException", "Artifact not found"))
            raise UserException(
                NameError(
                    f"{msg} not found. Perhaps there was a typo. Please try lineapy.catalog() to inspect all your artifacts."
                )
            )
        return res

    def get_all_artifacts(self) -> List[ArtifactORM]:
        """
        Used by the catalog to get all the artifacts
        """
        results = self.session.query(ArtifactORM).all()
        return results

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

    def get_source_code_for_session(self, session_id: LineaID) -> str:
        if (
            self.get_session_context(session_id).environment_type.name
            == "JUPYTER"
        ):
            jupyter_source_code_orms = (
                self.session.query(SourceCodeORM)
                .filter(SourceCodeORM.jupyter_session_id == session_id)
                .order_by(SourceCodeORM.jupyter_execution_count)
                .all()
            )
            return "".join(
                source_code.code for source_code in jupyter_source_code_orms
            )
        else:
            script_source_code_orms = (
                self.session.query(SourceCodeORM)
                .join(
                    BaseNodeORM, SourceCodeORM.id == BaseNodeORM.source_code_id
                )
                .filter(BaseNodeORM.session_id == session_id)
                .first()
            )
            return (
                script_source_code_orms.code
                if script_source_code_orms is not None
                else ""
            )
