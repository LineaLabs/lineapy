"""
User exposed objects through the :mod:`lineapy.apis`.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, cast

from IPython.display import display
from pandas.io.pickle import read_pickle

from lineapy.api.api_utils import de_lineate_code, extract_taskgraph
from lineapy.data.graph import Graph
from lineapy.data.types import LineaID, PipelineType
from lineapy.db.db import RelationalLineaDB
from lineapy.db.relational import (
    ArtifactDependencyORM,
    ArtifactORM,
    PipelineORM,
    SessionContextORM,
)
from lineapy.execution.context import get_context
from lineapy.execution.executor import Executor
from lineapy.graph_reader.program_slice import (
    get_slice_graph,
    get_source_code_from_graph,
)
from lineapy.plugins.airflow import AirflowDagConfig, AirflowPlugin
from lineapy.plugins.script import ScriptPlugin
from lineapy.plugins.task import TaskGraphEdge
from lineapy.utils.analytics.event_schemas import (
    ErrorType,
    ExceptionEvent,
    GetCodeEvent,
    GetValueEvent,
    GetVersionEvent,
    ToPipelineEvent,
)
from lineapy.utils.analytics.usage_tracking import track
from lineapy.utils.config import options
from lineapy.utils.deprecation_utils import lru_cache
from lineapy.utils.utils import get_new_id, prettify

logger = logging.getLogger(__name__)


@dataclass
class LineaArtifact:
    """LineaArtifact
    exposes functionalities we offer around the artifact.
    """

    db: RelationalLineaDB = field(repr=False)
    _execution_id: LineaID = field(repr=False)
    _node_id: LineaID = field(repr=False)
    """node id of the artifact in the graph"""
    _session_id: LineaID = field(repr=False)
    """session id of the session that created the artifact"""
    name: str
    """name of the artifact"""
    _version: int
    """version of the artifact - currently start from 0"""
    date_created: Optional[datetime] = field(default=None, repr=False)
    # setting repr to false for date_created for now since it duplicates version
    """Optional because date_created cannot be set by the user. 
    it is supposed to be automatically set when the artifact gets saved to the 
    db. so when creating lineaArtifact the first time, it will be unset. When 
    you get the artifact or list of artifacts as an artifact store, we retrieve 
    the date from db directly"""

    @property
    def version(self) -> int:
        track(GetVersionEvent(""))
        return self._version

    @lru_cache(maxsize=None)
    def get_value(self) -> object:
        """
        Get and return the value of the artifact
        """
        pickle_filename = self.db.get_node_value_path(
            self._node_id, self._execution_id
        )
        if pickle_filename is None:
            return None
        else:
            # TODO - set unicode etc here
            track(GetValueEvent(has_value=True))

            artifact_storage_dir = options.safe_get("artifact_storage_dir")
            filepath = (
                artifact_storage_dir.joinpath(pickle_filename)
                if isinstance(artifact_storage_dir, Path)
                else f'{artifact_storage_dir.rstrip("/")}/{pickle_filename}'
            )
            try:
                logger.debug(
                    f"Retriving pickle file from {filepath} ",
                )
                return read_pickle(
                    filepath, storage_options=options.get("storage_options")
                )
            except Exception as e:
                logger.error(e)
                track(
                    ExceptionEvent(
                        ErrorType.RETRIEVE, "Error in retriving pickle file"
                    )
                )
                raise e

    # Note that I removed the @properties because they were not working
    # well with the lru_cache
    @lru_cache(maxsize=None)
    def _get_subgraph(self, keep_lineapy_save: bool = False) -> Graph:
        """
        Return the slice subgraph for the artifact.

        :param keep_lineapy_save: Whether to retain ``lineapy.save()`` in code slice.
                Defaults to ``False``.

        """
        return get_slice_graph(
            self._get_graph(), [self._node_id], keep_lineapy_save
        )

    @lru_cache(maxsize=None)
    def get_code(
        self,
        use_lineapy_serialization: bool = True,
        keep_lineapy_save: bool = False,
    ) -> str:
        """
        Return the slices code for the artifact

        :param use_lineapy_serialization: If ``True``, will use the lineapy serialization to get the code.
                We will hide the serialization and the value pickler irrespective of the value type.
                If ``False``, will use remove all the lineapy references and instead use the underlying serializer directly.
                Currently, we use the native ``pickle`` serializer.
        :param keep_lineapy_save: Whether to retain ``lineapy.save()`` in code slice.
                Defaults to ``False``.

        """
        # FIXME: this seems a little heavy to just get the slice?
        track(
            GetCodeEvent(
                use_lineapy_serialization=use_lineapy_serialization,
                is_session_code=False,
            )
        )
        code = str(
            get_source_code_from_graph(self._get_subgraph(keep_lineapy_save))
        )
        if not use_lineapy_serialization:
            code = de_lineate_code(code, self.db)
        return prettify(code)

    @lru_cache(maxsize=None)
    def get_session_code(self, use_lineapy_serialization=True) -> str:
        """
        Return the raw session code for the artifact. This will include any
        comments and non-code lines.

        :param use_lineapy_serialization: If ``True``, will use the lineapy serialization to get the code.
                We will hide the serialization and the value pickler irrespective of the value type.
                If ``False``, will use remove all the lineapy references and instead use the underlying serializer directly.
                Currently, we use the native ``pickle`` serializer.

        """
        # using this over get_source_code_from_graph because it will process the
        # graph code and not return the original code with comments etc.
        track(
            GetCodeEvent(
                use_lineapy_serialization=use_lineapy_serialization,
                is_session_code=True,
            )
        )
        code = self.db.get_source_code_for_session(self._session_id)
        if not use_lineapy_serialization:
            code = de_lineate_code(code, self.db)
        # NOTE: we are not prettifying this code because we want to preserve what
        # the user wrote originally, without processing
        return code

    @lru_cache(maxsize=None)
    def _get_graph(self) -> Graph:
        session_context = self.db.get_session_context(self._session_id)
        # FIXME: copied cover from tracer, we might want to refactor
        nodes = self.db.get_nodes_for_session(self._session_id)
        return Graph(nodes, session_context)

    def visualize(self, path: Optional[str] = None) -> None:
        """
        Displays the graph for this artifact.

        If a path is provided, will save it to that file instead.
        """
        # adding this inside function to lazy import graphviz.
        # This way we can import lineapy without having graphviz installed.
        from lineapy.visualizer import Visualizer

        visualizer = Visualizer.for_public_node(
            self._get_graph(), self._node_id
        )
        if path:
            visualizer.render_pdf_file(path)
        else:
            display(visualizer.ipython_display_object())

    def execute(self) -> object:
        """
        Executes the artifact graph.

        """
        slice_exec = Executor(self.db, globals())
        slice_exec.execute_graph(self._get_subgraph())
        return slice_exec.get_value(self._node_id)


class LineaArtifactStore:
    """LineaArtifactStore

    A simple way to access meta data about artifacts in Linea.
    """

    """
    .. note::

        - The export is pretty limited right now and we should expand later.

    """

    def __init__(self, db):
        db_artifacts: List[ArtifactORM] = db.get_all_artifacts()
        self.artifacts: List[LineaArtifact] = [
            LineaArtifact(
                db=db,
                _execution_id=db_artifact.execution_id,
                _node_id=db_artifact.node_id,
                _session_id=db_artifact.node.session_id,
                _version=db_artifact.version,  # type: ignore
                name=cast(str, db_artifact.name),
                date_created=db_artifact.date_created,  # type: ignore
            )
            for db_artifact in db_artifacts
        ]

    @property
    def len(self) -> int:
        return len(self.artifacts)

    @property
    def print(self) -> str:
        # Can't really cache this since the values might change
        return "\n".join(
            [
                f"{a.name}:{a.version} created on {a.date_created}"
                for a in self.artifacts
            ]
        )

    def __str__(self) -> str:
        return self.print

    def __repr__(self) -> str:
        return self.print

    @property
    def export(self):
        """
        :return: a dictionary of artifact information, which the user can then
            manipulate with their favorite dataframe tools, such as pandas,
            e.g., `cat_df = pd.DataFrame(artifact_store.export())`.
        """
        return [
            {
                "artifact_name": a.name,
                "artifact_version": a.version,
                "date_created": a.date_created,
            }
            for a in self.artifacts
        ]


class Pipeline:
    def __init__(
        self,
        artifacts: List[str],
        name: Optional[str] = None,
        dependencies: TaskGraphEdge = {},
    ):
        self.dependencies = dependencies
        self.artifact_safe_names, self.task_graph = extract_taskgraph(
            artifacts, dependencies
        )
        self.name = name or "_".join(self.artifact_safe_names)
        self.artifact_names: List[str] = artifacts
        self.id = get_new_id()

    def export(
        self,
        framework: str = "SCRIPT",
        output_dir: Optional[str] = None,
        pipeline_dag_config: Optional[AirflowDagConfig] = {},
    ) -> Path:
        execution_context = get_context()
        db = execution_context.executor.db
        session_orm = (
            db.session.query(SessionContextORM)
            .order_by(SessionContextORM.creation_time.desc())
            .all()
        )
        if len(session_orm) == 0:
            track(ExceptionEvent(ErrorType.PIPELINE, "No session found in DB"))
            raise Exception("No sessions found in the database.")
        last_session = session_orm[0]

        if framework in PipelineType.__members__:
            if PipelineType[framework] == PipelineType.AIRFLOW:

                ret = AirflowPlugin(db, last_session.id).sliced_airflow_dag(
                    self.name,
                    self.task_graph,
                    output_dir=output_dir,
                    airflow_dag_config=pipeline_dag_config,
                )

            else:

                ret = ScriptPlugin(db, last_session.id).sliced_pipeline_dag(
                    self.name,
                    self.task_graph,
                    output_dir=output_dir,
                )

            # send the info
            track(
                ToPipelineEvent(
                    framework,
                    len(self.artifact_names),
                    self.task_graph.get_airflow_dependency() != "",
                    pipeline_dag_config is not None,
                )
            )
            return ret

        else:
            raise Exception(f"No PipelineType for {framework}")

    def save(self):
        # TODO save this pipeline to the db using PipelineORM
        execution_context = get_context()
        db = execution_context.executor.db
        session_orm = (
            db.session.query(SessionContextORM)
            .order_by(SessionContextORM.creation_time.desc())
            .all()
        )
        if len(session_orm) == 0:
            track(ExceptionEvent(ErrorType.PIPELINE, "No session found in DB"))
            raise Exception("No sessions found in the database.")
        last_session = session_orm[0]

        artifacts_to_save = [
            db.get_artifact_by_name(artifact_name)
            for artifact_name in self.artifact_names
        ]

        art_deps_to_save = []
        for post_artifact, pre_artifacts in self.dependencies.items():
            post_to_save = db.get_artifact_by_name(post_artifact)
            pre_to_save = [db.get_artifact_by_name(a) for a in pre_artifacts]
            art_dep_to_save = ArtifactDependencyORM(
                post_artifact=post_to_save, pre_artifacts=pre_to_save
            )
            art_deps_to_save.append(art_dep_to_save)

        pipeline_to_write = PipelineORM(
            name=self.name,
            artifacts=artifacts_to_save,
            dependencies=art_deps_to_save,
        )
        db.write_pipeline(art_deps_to_save, pipeline_to_write)
