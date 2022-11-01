from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Set, Tuple, Union

from IPython.display import display
from pandas.io.pickle import read_pickle

from lineapy.api.api_utils import de_lineate_code
from lineapy.data.graph import Graph
from lineapy.data.types import (
    ARTIFACT_STORAGE_BACKEND,
    ArtifactInfo,
    LineaArtifactDef,
    LineaArtifactInfo,
    LineaID,
    MLflowArtifactInfo,
)
from lineapy.db.db import ArtifactORM, RelationalLineaDB
from lineapy.execution.executor import Executor
from lineapy.graph_reader.program_slice import (
    get_slice_graph,
    get_source_code_from_graph,
    get_subgraph_nodelist,
)
from lineapy.plugins.serializers.mlflow_io import read_mlflow
from lineapy.utils.analytics.event_schemas import (
    ErrorType,
    ExceptionEvent,
    GetCodeEvent,
    GetValueEvent,
    GetVersionEvent,
)
from lineapy.utils.analytics.usage_tracking import track
from lineapy.utils.config import options
from lineapy.utils.deprecation_utils import lru_cache
from lineapy.utils.utils import prettify

logger = logging.getLogger(__name__)


def get_lineaartifactdef(
    art_entry: Union[str, Tuple[str, Optional[int]]]
) -> LineaArtifactDef:
    """
    Convert artifact entry (string) or (string, integer) to LineaArtifactDef
    """
    args: LineaArtifactDef
    if isinstance(art_entry, str):
        args = {"artifact_name": art_entry}
    elif isinstance(art_entry, tuple):
        args = {"artifact_name": art_entry[0], "version": art_entry[1]}
    else:
        raise ValueError(
            "An artifact should be passed in as a string or (string, integer) tuple."
        )
    return args


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
    _artifact_id: Optional[int] = field(default=None, repr=False)
    date_created: Optional[datetime] = field(default=None, repr=False)
    # setting repr to false for date_created, _artifact_id for now since it duplicates version
    """Optional because date_created and _artifact_id cannot be set by the user. 
    it is supposed to be automatically set when the artifact gets saved to the 
    db. so when creating lineaArtifact the first time, it will be unset. When 
    you get the artifact or list of artifacts as an artifact store, we retrieve 
    the date from db directly"""

    @property
    def version(self) -> int:
        track(GetVersionEvent(""))
        return self._version

    @property
    def node_id(self) -> LineaID:
        return self._node_id

    @property
    def session_id(self) -> LineaID:
        return self._session_id

    @lru_cache(maxsize=None)
    def get_value(self) -> object:
        """
        Get and return the value of the artifact
        """
        metadata = self.get_metadata()
        linea_metadata = metadata["lineapy"]
        saved_filepath = linea_metadata.storage_path
        if saved_filepath is None:
            return None
        else:
            track(GetValueEvent(has_value=True))
            # read from mlflow
            if "mlflow" in metadata.keys():
                return read_mlflow(metadata["mlflow"])

            # read from lineapy
            return self._read_pickle(saved_filepath)

    @lru_cache(maxsize=None)
    def _get_storage_path(self) -> Optional[str]:
        return self.db.get_node_value_path(self._node_id, self._execution_id)

    @lru_cache(maxsize=None)
    def get_metadata(self, lineapy_only: bool = False) -> ArtifactInfo:
        """
        Get artifact backend storage metadata

        :param lineapy_only: If ``False``, will include both LineaPy related
            metadata and metadata from storage backend(if it is not LineaPy).
            If ``True``, will only return LineaPy related metadata no matter
            which storage backend is using.

        :return: Metadata for artifact backend storage.

        """

        if self._artifact_id is None or self.date_created is None:
            artifactorm = self.db.get_artifactorm_by_name(
                artifact_name=self.name, version=self.version
            )
            self._artifact_id = artifactorm.id
            self.date_created = artifactorm.date_created

        assert isinstance(self._artifact_id, int)
        assert isinstance(self.date_created, datetime)

        storage_path = self._get_storage_path()
        storage_backend = (
            ARTIFACT_STORAGE_BACKEND.mlflow
            if isinstance(storage_path, str)
            and storage_path.startswith("runs:")
            else ARTIFACT_STORAGE_BACKEND.lineapy
        )

        lineaartifact_metadata = LineaArtifactInfo(
            artifact_id=self._artifact_id,
            name=self.name,
            version=self.version,
            execution_id=self._execution_id,
            session_id=self._session_id,
            node_id=self._node_id,
            date_created=self.date_created,
            storage_path=storage_path,
            storage_backend=storage_backend,
        )

        metadata = ArtifactInfo(lineapy=lineaartifact_metadata)

        if not lineapy_only and storage_backend == "mlflow":
            mlflowartifactorm = (
                self.db.get_mlflowartifactmetadataorm_by_artifact_id(
                    self._artifact_id
                )
            )
            assert isinstance(mlflowartifactorm.id, int)
            assert isinstance(mlflowartifactorm.artifact_id, int)
            assert isinstance(mlflowartifactorm.tracking_uri, str)
            assert isinstance(mlflowartifactorm.model_uri, str)
            assert isinstance(mlflowartifactorm.model_flavor, str)
            metadata["mlflow"] = MLflowArtifactInfo(
                id=mlflowartifactorm.id,
                artifact_id=mlflowartifactorm.artifact_id,
                tracking_uri=mlflowartifactorm.tracking_uri,
                registry_uri=mlflowartifactorm.registry_uri,
                model_uri=mlflowartifactorm.model_uri,
                model_flavor=mlflowartifactorm.model_flavor,
            )

        return metadata

    def _read_pickle(self, pickle_filename):
        """
        Read pickle file from artifact storage dir
        """
        # TODO - set unicode etc here
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
        session_graph = Graph.create_session_graph(self.db, self._session_id)
        return get_slice_graph(
            session_graph, [self._node_id], keep_lineapy_save
        )

    @lru_cache(maxsize=None)
    def _get_sessiongraph_and_subgraph_nodelist(
        self, keep_lineapy_save: bool = False
    ) -> Tuple[Graph, Set[LineaID]]:
        session_graph = Graph.create_session_graph(self.db, self._session_id)
        return session_graph, get_subgraph_nodelist(
            session_graph, [self._node_id], keep_lineapy_save
        )

    @lru_cache(maxsize=None)
    def get_code(
        self,
        use_lineapy_serialization: bool = True,
        keep_lineapy_save: bool = False,
        include_non_slice_as_comment: bool = False,
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
        (
            sessiongraph,
            subgraph_nodelist,
        ) = self._get_sessiongraph_and_subgraph_nodelist(keep_lineapy_save)
        code = str(
            get_source_code_from_graph(
                subgraph_nodelist,
                session_graph=sessiongraph,
                include_non_slice_as_comment=include_non_slice_as_comment,
            )
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

    def visualize(self, path: Optional[str] = None) -> None:
        """
        Displays the graph for this artifact.

        If a path is provided, will save it to that file instead.
        """
        # adding this inside function to lazy import graphviz.
        # This way we can import lineapy without having graphviz installed.
        from lineapy.visualizer import Visualizer

        session_graph = Graph.create_session_graph(self.db, self._session_id)
        visualizer = Visualizer.for_public_node(session_graph, self._node_id)
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

    @staticmethod
    def get_artifact_from_orm(
        db: RelationalLineaDB, artifactorm: ArtifactORM
    ) -> LineaArtifact:
        """
        Return LineaArtifact from artifactorm
        """
        assert isinstance(artifactorm.name, str)
        return LineaArtifact(
            db=db,
            _artifact_id=artifactorm.id,
            _execution_id=artifactorm.execution_id,
            _node_id=artifactorm.node_id,
            _session_id=artifactorm.node.session_id,
            _version=artifactorm.version,  # type: ignore
            name=artifactorm.name,
            date_created=artifactorm.date_created,  # type: ignore
        )

    @staticmethod
    def get_artifact_from_name_and_version(
        db: RelationalLineaDB,
        artifact_name: str,
        version: Optional[int] = None,
    ) -> LineaArtifact:
        """
        Return LineaArtifact from artifact name and version
        """
        return LineaArtifact.get_artifact_from_orm(
            db, db.get_artifactorm_by_name(artifact_name, version)
        )

    @staticmethod
    def get_artifact_from_def(
        db: RelationalLineaDB, artifactdef: LineaArtifactDef
    ) -> LineaArtifact:
        """
        Return LineaArtifact from LineaArtifactDef
        """
        return LineaArtifact.get_artifact_from_name_and_version(
            db, **artifactdef
        )
