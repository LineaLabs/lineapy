from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from IPython.display import display
from pandas.io.pickle import read_pickle

from lineapy.api.api_utils import de_lineate_code
from lineapy.data.graph import Graph
from lineapy.data.types import LineaID
from lineapy.db.db import ArtifactORM, RelationalLineaDB
from lineapy.execution.executor import Executor
from lineapy.graph_reader.program_slice import (
    get_slice_graph,
    get_source_code_from_graph,
)
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
        session_graph = Graph.create_session_graph(self.db, self._session_id)
        return get_slice_graph(
            session_graph, [self._node_id], keep_lineapy_save
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
    def get_artifact_from_db_and_artifactorm(
        db: RelationalLineaDB, artifactorm: ArtifactORM
    ) -> LineaArtifact:
        """
        Return LineaArtifact from artifactorm
        """
        return LineaArtifact(
            db=db,
            _execution_id=artifactorm.execution_id,
            _node_id=artifactorm.node_id,
            _session_id=artifactorm.node.session_id,
            _version=artifactorm.version,  # type: ignore
            name=artifactorm.name,
            date_created=artifactorm.date_created,  # type: ignore
        )

    @staticmethod
    def get_artifact_from_db_name_and_version(
        db: RelationalLineaDB,
        artifact_name: str,
        version: Optional[int] = None,
    ) -> LineaArtifact:
        """
        Return LineaArtifact from artifact name and version
        """
        return LineaArtifact.get_artifact_from_db_and_artifactorm(
            db, db.get_artifactorm_by_name(artifact_name, version)
        )
