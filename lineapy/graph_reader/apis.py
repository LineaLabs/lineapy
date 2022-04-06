"""
User exposed objects through the :mod:`lineapy.apis`.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, cast

from IPython.display import display

from lineapy.data.graph import Graph
from lineapy.data.types import LineaID
from lineapy.db.db import RelationalLineaDB
from lineapy.db.relational import ArtifactORM
from lineapy.execution.executor import Executor
from lineapy.graph_reader.program_slice import (
    get_slice_graph,
    get_source_code_from_graph,
)
from lineapy.utils.constants import VERSION_DATE_STRING, VERSION_PLACEHOLDER

logger = logging.getLogger(__name__)


@dataclass
class LineaArtifact:
    """LineaArtifact
    exposes functionalities we offer around the artifact.
    """

    db: RelationalLineaDB = field(repr=False)
    execution_id: LineaID
    node_id: LineaID
    """node id of the artifact in the graph"""
    session_id: LineaID
    """session id of the session that created the artifact"""
    name: str
    """name of the artifact"""
    date_created: Optional[datetime] = field(default=None)
    """Optional because date_created cannot be set by the user. 
    it is supposed to be automatically set when the 
    artifact gets saved to the db. so when creating lineaArtifact 
    the first time, it will be unset. When you get the artifact or 
    catalog of artifacts, we retrieve the date from db and 
    it will be set."""
    version: str = field(init=False, repr=False)
    """version of the artifact - This is set when the artifact is saved. The format of the version currently is specified by the constant :const:`lineapy.utils.constants.VERSION_DATE_STRING`"""

    def __post_init__(self):
        self.version = datetime.now().strftime(VERSION_DATE_STRING)

    @property
    def value(self) -> object:
        """
        Get and return the value of the artifact
        """
        value = self.db.get_node_value_from_db(self.node_id, self.execution_id)
        if not value:
            raise ValueError("No value saved for this node")
        return value.value

    @property
    def _subgraph(self) -> Graph:
        """
        Return the slice subgraph for the artifact
        """
        return get_slice_graph(self._graph, [self.node_id])

    @property
    def code(self) -> str:
        """
        Return the slices code for the artifact
        """
        # FIXME: this seems a little heavy to just get the slice?
        return get_source_code_from_graph(self._subgraph)

    @property
    def _graph(self) -> Graph:
        session_context = self.db.get_session_context(self.session_id)
        # FIXME: copied cover from tracer, we might want to refactor
        nodes = self.db.get_nodes_for_session(self.session_id)
        return Graph(nodes, session_context)

    def visualize(self, path: Optional[str] = None) -> None:
        """
        Displays the graph for this artifact.

        If a path is provided, will save it to that file instead.
        """
        # adding this inside function to lazy import graphviz.
        # This way we can import lineapy without having graphviz installed.
        from lineapy.visualizer import Visualizer

        visualizer = Visualizer.for_public_node(self._graph, self.node_id)
        if path:
            visualizer.render_pdf_file(path)
        else:
            display(visualizer.ipython_display_object())

    def execute(self) -> object:
        """
        Executes the artifact graph.

        """
        slice_exec = Executor(self.db, globals())
        slice_exec.execute_graph(self._subgraph)
        return slice_exec.get_value(self.node_id)


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
        self.artifacts: List[LineaArtifact] = []
        for db_artifact in db_artifacts:
            l_artifact = LineaArtifact(
                db=db,
                execution_id=db_artifact.execution_id,
                node_id=db_artifact.node_id,
                session_id=db_artifact.node.session_id,
                name=cast(str, db_artifact.name),
                date_created=db_artifact.date_created,
            )
            l_artifact.version = db_artifact.version or VERSION_PLACEHOLDER
            self.artifacts.append(l_artifact)

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
