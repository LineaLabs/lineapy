"""
User exposed objects through the :mod:`lineapy.apis`.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, cast

from IPython.display import display

from lineapy.data.graph import Graph
from lineapy.data.types import LineaID
from lineapy.db.db import RelationalLineaDB
from lineapy.db.relational import ArtifactORM
from lineapy.db.utils import FilePickler
from lineapy.execution.executor import Executor
from lineapy.graph_reader.program_slice import (
    get_slice_graph,
    get_source_code_from_graph,
)
from lineapy.utils.analytics import (
    GetCodeEvent,
    GetValueEvent,
    GetVersionEvent,
    track,
)
from lineapy.utils.deprecation_utils import lru_cache

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
    _version: str
    """version of the artifact - This is set when the artifact is saved. The format of the version currently is specified by the constant :const:`lineapy.utils.constants.VERSION_DATE_STRING`"""
    date_created: Optional[datetime] = field(default=None, repr=False)
    # setting repr to false for date_created for now since it duplicates version
    """Optional because date_created cannot be set by the user. 
    it is supposed to be automatically set when the 
    artifact gets saved to the db. so when creating lineaArtifact 
    the first time, it will be unset. When you get the artifact or 
    catalog of artifacts, we retrieve the date from db and 
    it will be set."""

    @property
    def version(self) -> str:
        track(GetVersionEvent(""))
        return self._version

    @lru_cache(maxsize=None)
    def get_value(self) -> object:
        """
        Get and return the value of the artifact
        """
        value = self._get_value_path()
        if value is None:
            return None
        else:
            # TODO - set unicode etc here
            track(GetValueEvent(has_value=True))
            with open(value, "rb") as f:
                return FilePickler.load(f)

    def _get_value_path(
        self, other: Optional[ArtifactORM] = None
    ) -> Optional[str]:
        """
        Get the path to the value of the artifact.
        :param other: Additional argument to let you query another artifact's value path.
                      This is set to be optional and if its not set, we will use the current artifact
        """
        if other is not None:
            value = self.db.get_node_value_from_db(
                other.node_id, other.execution_id
            )
        else:
            value = self.db.get_node_value_from_db(
                self._node_id, self._execution_id
            )
        if not value:
            raise ValueError("No value saved for this node")
        return value.value

    # Note that I removed the @properties becuase they were not working
    # well with the lru_cache
    @lru_cache(maxsize=None)
    def _get_subgraph(self) -> Graph:
        """
        Return the slice subgraph for the artifact
        """
        return get_slice_graph(self._get_graph(), [self._node_id])

    @lru_cache(maxsize=None)
    def get_code(self, use_lineapy_serialization=True) -> str:
        """
        Return the slices code for the artifact
        """
        # FIXME: this seems a little heavy to just get the slice?
        track(
            GetCodeEvent(use_lineapy_serialization=True, is_session_code=False)
        )
        return self._de_linealize_code(
            get_source_code_from_graph(self._get_subgraph()),
            use_lineapy_serialization,
        )

    @lru_cache(maxsize=None)
    def get_session_code(self, use_lineapy_serialization=True) -> str:
        """
        Return the raw session code for the artifact. This will include any
        comments and non-code lines.
        """
        # using this over get_source_code_from_graph because it will process the
        # graph code and not return the original code with comments etc.
        track(
            GetCodeEvent(use_lineapy_serialization=False, is_session_code=True)
        )
        return self._de_linealize_code(
            self.db.get_source_code_for_session(self._session_id),
            use_lineapy_serialization,
        )

    def _de_linealize_code(
        self, code: str, use_lineapy_serialization: bool
    ) -> str:
        """
        De-linealize the code by removing any lineapy api references
        """
        if use_lineapy_serialization:
            return code
        else:
            lineapy_pattern = re.compile(
                r"(lineapy.(save\(([\w]+),\s*[\"\']([\w\-\s]+)[\"\']\)|get\([\"\']([\w\-\s]+)[\"\']\).get_value\(\)))"
            )
            # init swapped version

            def replace_fun(match):
                if match.group(2).startswith("save"):
                    # TODO - this can be another artifact. find it using the match.group(4)
                    # dep_artifact = self.db.get_artifact_by_name(match.group(4))
                    path_to_use = self._get_value_path()
                    return f'pickle.dump({match.group(3)},open("{path_to_use}","wb"))'

                elif match.group(2).startswith("get"):
                    # this typically will be a different artifact.
                    dep_artifact = self.db.get_artifact_by_name(match.group(5))
                    path_to_use = self._get_value_path(dep_artifact)
                    return f'pickle.load(open("{path_to_use}","rb"))'

            swapped, replaces = lineapy_pattern.subn(replace_fun, code)
            if replaces > 0:
                # If we replaced something, pickle was used so add import pickle on top
                # Conversely, if lineapy reference was removed, potentially the import lineapy line is not needed anymore.
                remove_pattern = re.compile(r"import lineapy\n")
                match_pattern = re.compile(r"lineapy\.(.*)")
                swapped = "import pickle\n" + swapped
                if match_pattern.search(swapped):
                    # we still are using lineapy.xxx functions
                    # so do nothing
                    pass
                else:
                    swapped, lineareplaces = remove_pattern.subn("", swapped)
                    logger.debug(f"Removed lineapy {lineareplaces} times")

            logger.debug("replaces made: %s", replaces)

            return swapped

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


class LineaCatalog:
    """LineaCatalog

    A simple way to access meta data about artifacts in Linea
    """

    """
    DEV NOTE:
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
        Returns
        -------
            a dictionary of artifact information, which the user can then
            manipulate with their favorite dataframe tools, such as pandas,
            e.g., `cat_df = pd.DataFrame(catalog.export())`.
        """
        return [
            {
                "artifact_name": a.name,
                "artifact_version": a.version,
                "date_created": a.date_created,
            }
            for a in self.artifacts
        ]
