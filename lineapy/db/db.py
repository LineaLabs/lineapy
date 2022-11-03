from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from sqlalchemy.orm import defaultload, scoped_session, sessionmaker
from sqlalchemy.sql.expression import and_

from lineapy.data.types import (
    Artifact,
    CallNode,
    ElseNode,
    Execution,
    GlobalNode,
    IfNode,
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
    ArtifactDependencyORM,
    ArtifactORM,
    Base,
    BaseNodeORM,
    CallNodeORM,
    ElseNodeORM,
    ExecutionORM,
    GlobalNodeORM,
    GlobalReferenceORM,
    IfNodeORM,
    ImplicitDependencyORM,
    ImportNodeORM,
    KeywordArgORM,
    LiteralNodeORM,
    LookupNodeORM,
    MLflowArtifactMetadataORM,
    MutateNodeORM,
    NodeORM,
    NodeValueORM,
    PipelineORM,
    PositionalArgORM,
    SessionContextORM,
    SourceCodeORM,
    VariableNodeORM,
)
from lineapy.db.utils import create_lineadb_engine
from lineapy.exceptions.db_exceptions import ArtifactSaveException
from lineapy.exceptions.user_exception import UserException
from lineapy.utils.analytics.event_schemas import ErrorType, ExceptionEvent
from lineapy.utils.analytics.usage_tracking import track  # circular dep issues
from lineapy.utils.config import lineapy_config, options
from lineapy.utils.constants import DB_SQLITE_PREFIX
from lineapy.utils.utils import get_literal_value_from_string

if "mlflow" in sys.modules:
    from mlflow.models.model import ModelInfo

logger = logging.getLogger(__name__)


class RelationalLineaDB:
    """
    - Note that LineaDB coordinates with asset manager and relational db.

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
        self.engine = create_lineadb_engine(self.url)
        self.session = scoped_session(sessionmaker())
        self.session.configure(bind=self.engine)
        from alembic import command
        from alembic.config import Config
        from sqlalchemy import inspect

        lp_install_dir = Path(__file__).resolve().parent.parent

        alembic_cfg = Config((lp_install_dir / "alembic.ini").as_posix())
        alembic_cfg.set_main_option(
            "script_location", (lp_install_dir / "_alembic").as_posix()
        )
        alembic_cfg.set_main_option("sqlalchemy.url", self.url)
        if not inspect(self.engine).get_table_names():
            # No tables in the database, so create them
            Base.metadata.create_all(self.engine)
            # stamp the database with the latest alembic db version for migration
            # https://alembic.sqlalchemy.org/en/latest/cookbook.html#building-an-up-to-date-database-from-scratch
            command.stamp(alembic_cfg, "head")
        else:
            # Tables exist, so upgrade the database
            command.upgrade(alembic_cfg, "head")

    def renew_session(self):
        if self.url.startswith(DB_SQLITE_PREFIX):
            self.commit()
            self.session = scoped_session(sessionmaker())
            self.session.configure(bind=self.engine)

    @classmethod
    def from_config(cls, options: lineapy_config) -> RelationalLineaDB:
        """
        Creates a new database.

        If no url is provided, it will use the result of ``lineapy_config.safe_get("database_url")``
        """
        return cls(str(options.safe_get("database_url")))

    @classmethod
    def from_environment(cls, url: str) -> RelationalLineaDB:
        """
        Creates a new database.

        If no url is provided, it will use the result of ``lineapy_config.safe_get("database_url")``
        """
        return cls(url)

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
        elif isinstance(val, bytes):
            return LiteralType.Bytes
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
            logger.debug(e)
            track(ExceptionEvent(ErrorType.DATABASE, "Failed commit"))
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
        args = node.dict(
            include={"id", "session_id", "node_type", "control_dependency"}
        )
        # Converting list into string, for storage in the DB. Note there can only be one or zero control dependencies
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
        elif isinstance(node, IfNode):
            node_orm = IfNodeORM(
                **args,
                test_id=node.test_id,
                unexec_id=node.unexec_id,
                companion_id=node.companion_id,
            )
        elif isinstance(node, ElseNode):
            node_orm = ElseNodeORM(
                **args,
                companion_id=node.companion_id,
                unexec_id=node.unexec_id,
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

    def write_assigned_variable(
        self,
        node_id: LineaID,
        variable_name: str,
    ) -> None:
        try:
            self.session.add(
                VariableNodeORM(id=node_id, variable_name=variable_name)
            )
            self.renew_session()
        except Exception as e:
            logger.info(
                "%s has been defined at node %s before; most likely you have imported the library before.",
                variable_name,
                node_id,
            )

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

    def write_mlflow_artifactmetadata(
        self, artifactorm: ArtifactORM, modelinfo: ModelInfo
    ) -> None:
        """
        Write MLflow metadata for the artifact
        """
        model_flavors = [
            flavor
            for flavor in modelinfo.flavors.keys()
            if flavor != "python_function"
        ]
        if len(model_flavors) > 1:
            msg = "Currently, only one MLflow model flavor(other than python_function) is supported."
            raise NotImplementedError(msg)

        mlflowmetadataorm = MLflowArtifactMetadataORM(
            artifact_id=artifactorm.id,
            backend="mlflow",
            tracking_uri=options.get("mlflow_tracking_uri"),
            registry_uri=options.get("mlflow_registry_uri"),
            model_uri=modelinfo.model_uri,
            model_flavor=model_flavors[0],
        )
        self.session.add(mlflowmetadataorm)
        self.renew_session()

    def write_pipeline(
        self, dependencies: List[ArtifactDependencyORM], pipeline: PipelineORM
    ) -> None:
        for dep in dependencies:
            self.session.add(dep)
        self.session.add(pipeline)
        self.renew_session()

    def get_pipeline_by_name(self, name: str) -> PipelineORM:

        res = (
            self.session.query(PipelineORM)
            .filter(PipelineORM.name == name)
            .first()
        )
        if res is None:
            msg = f"Pipeline {name} not found."
            track(ExceptionEvent(ErrorType.USER, "Pipeline not found"))
            raise UserException(NameError(msg))
        return res

    def artifact_in_db(
        self, node_id: LineaID, execution_id: LineaID, name: str, version: int
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
            "control_dependency": node.control_dependency,
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
        if isinstance(node, IfNodeORM):
            return IfNode(
                unexec_id=node.unexec_id,
                test_id=node.test_id,
                companion_id=node.companion_id,
                **args,
            )
        if isinstance(node, ElseNodeORM):
            return ElseNode(
                unexec_id=node.unexec_id,
                companion_id=node.companion_id,
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

    def get_node_value_path(
        self, node_id: LineaID, execution_id: LineaID
    ) -> Optional[str]:
        """
        Get the path to the value of the artifact.

        :param other: Additional argument to let you query another artifact's value path.
            This is set to be optional and if its not set, we will use the current artifact
        """
        value = self.get_node_value_from_db(node_id, execution_id)
        if not value:
            track(
                ExceptionEvent(
                    ErrorType.DATABASE, "Value path not found for the node"
                )
            )
            raise ValueError("No value saved for this node")
        return value.value

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

    def number_of_artifacts_per_node(
        self, node_id: LineaID, execution_id: LineaID
    ) -> int:
        """
        Returns number of artifacts that refer to
        the same execution node.
        """
        return (
            self.session.query(ArtifactORM)
            .filter(
                and_(
                    ArtifactORM.node_id == node_id,
                    ArtifactORM.execution_id == execution_id,
                )
            )
            .count()
        )

    def get_libraries_for_session(
        self, session_id: LineaID
    ) -> List[ImportNodeORM]:
        """
        Gets all dependencies for a session, assuming all the libs in a
        particular session will be required to set up a new env.

        """
        return (
            self.session.query(
                ImportNodeORM.package_name, ImportNodeORM.version
            )
            .filter(
                and_(
                    ImportNodeORM.session_id == session_id,
                    ImportNodeORM.package_name != "None",
                    ImportNodeORM.version != "None",
                )
            )
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

    def get_artifactorm_by_name(
        self, artifact_name: str, version: Optional[int] = None
    ) -> ArtifactORM:
        """
        Gets the most recent artifact with a certain name.
        If a version is not specified, it will return the most recent
        version sorted by date_created
        """
        res_query = self.session.query(ArtifactORM).filter(
            ArtifactORM.name == artifact_name
        )
        if version is not None:
            res_query = res_query.filter(ArtifactORM.version == version)
        res = res_query.order_by(ArtifactORM.version.desc()).first()
        if res is None:
            msg = (
                (
                    f"Artifact {artifact_name} (version {version})"
                    if version
                    else f"Artifact {artifact_name}"
                )
                + " not found. Perhaps there was a typo. Please try lineapy.artifact_store() to inspect all your artifacts."
            )
            track(ExceptionEvent(ErrorType.USER, "Artifact not found"))
            raise UserException(NameError(msg))
        return res

    def get_latest_artifact_version(self, artifact_name: str) -> int:
        """
        Get the latest version number of an artifact.
        If the artifact does not exist, it will return -1
        """
        res = (
            self.session.query(ArtifactORM)
            .filter(ArtifactORM.name == artifact_name)
            .order_by(ArtifactORM.version.desc())
            .first()
        )
        return -1 if res is None else res.version

    def get_all_artifacts(self) -> List[ArtifactORM]:
        """
        Used by the artifact store to get all the artifacts
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

    def delete_artifact_by_name(
        self, artifact_name: str, version: Union[int, str]
    ):
        """
        Deletes the most recent artifact with a certain name.
        If a version is not specified, it will delete the most recent
        version sorted by date_created
        """
        res_query = self.session.query(ArtifactORM).filter(
            ArtifactORM.name == artifact_name
        )
        if version == "all":
            res_query.delete()
        else:
            if isinstance(version, int):
                res_query = res_query.filter(ArtifactORM.version == version)
            res = res_query.order_by(ArtifactORM.version.desc()).first()
            if res is None:
                msg = (
                    (
                        f"Artifact {artifact_name} (version {version})"
                        if version
                        else f"Artifact {artifact_name}"
                    )
                    + " not found. Perhaps there was a typo. Please try lineapy.artifact_store() to inspect all your artifacts."
                )
                track(ExceptionEvent(ErrorType.USER, "Artifact not found"))
                raise UserException(NameError(msg))
            self.session.delete(res)
        self.renew_session()

    def delete_mlflow_metadata_by_artifact_id(self, artifact_id: int) -> None:
        """
        Delete MLflow metadata for the artifact

        Add current timestamp to delete_time to the mlflowartifactmetadata table
        """
        self.session.query(MLflowArtifactMetadataORM).filter(
            and_(
                MLflowArtifactMetadataORM.artifact_id == artifact_id,
                MLflowArtifactMetadataORM.delete_time.is_(None),
            )
        ).update({"delete_time": datetime.utcnow()})
        self.renew_session()

    def delete_node_value_from_db(
        self, node_id: LineaID, execution_id: LineaID
    ):
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
        if value_orm is None:
            track(
                ExceptionEvent(
                    ErrorType.DATABASE, "Value not found for the node"
                )
            )
            raise UserException(
                NameError(
                    f"NodeID {node_id} and ExecutionID {execution_id} does not exist"
                )
            )

        self.session.delete(value_orm)
        self.renew_session()

    def get_variable_by_id(self, linea_id: LineaID) -> List[str]:
        """
        Returns the variable names(as a list) for a node with a certain ID
        """

        variable_node_orm = (
            self.session.query(VariableNodeORM)
            .filter(VariableNodeORM.id == linea_id)
            .all()
        )
        return [n.variable_name for n in variable_node_orm]

    def get_variables_for_session(
        self, session_id: LineaID
    ) -> List[Tuple[LineaID, str]]:
        """
        Returns the variable names for a session, as (LineaID, variable_name)
        """

        results = (
            self.session.query(BaseNodeORM, VariableNodeORM)
            .join(
                VariableNodeORM,
                VariableNodeORM.id == BaseNodeORM.id,
                # isouter=None,
            )
            .filter(
                and_(
                    BaseNodeORM.id == VariableNodeORM.id,
                    BaseNodeORM.session_id == session_id,
                )
            )
            .all()
        )
        return [(n[0].id, n[1].variable_name) for n in results]

    def get_mlflowartifactmetadataorm_by_artifact_id(
        self, artifact_id: int
    ) -> MLflowArtifactMetadataORM:
        """
        Get MLflow metadata for the artifact
        """

        res_query = self.session.query(MLflowArtifactMetadataORM).filter(
            and_(
                MLflowArtifactMetadataORM.artifact_id == artifact_id,
                MLflowArtifactMetadataORM.delete_time.is_(None),
            )
        )
        return res_query.one()
