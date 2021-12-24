"""
User exposed APIs.
Should keep it very clean.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from functools import cached_property
from os import environ
from pathlib import Path
from typing import Optional

from IPython.display import display

from lineapy.data.graph import Graph
from lineapy.data.types import LineaID
from lineapy.db.db import RelationalLineaDB
from lineapy.db.relational import BaseNodeORM, SessionContextORM
from lineapy.graph_reader.program_slice import get_program_slice
from lineapy.plugins.airflow import to_airflow

logger = logging.getLogger(__name__)


@dataclass
class LineaArtifact:
    """LineaArtifact
    exposes functionalities we offer around the artifact.
    The current list is:
    - code
    - value
    """

    """
    DEV NOTE:
    - Currently versions is still confusing. We need to sort it our before
      we expose to users.
    """
    db: RelationalLineaDB = field(repr=False)
    execution_id: LineaID
    node_id: LineaID
    session_id: LineaID
    name: str

    @cached_property
    def value(self) -> object:
        """
        Get and return the value of the artifact
        """
        value = self.db.get_node_value_from_db(self.node_id, self.execution_id)
        if not value:
            raise ValueError("No value saved for this node")
        return value.value

    @cached_property
    def code(self) -> str:
        """
        Return the slices code for the artifact
        """
        # FIXME: this seems a little heavy to just get the slice?
        return get_program_slice(self._graph, [self.node_id])

    @cached_property
    def _graph(self) -> Graph:
        session_context = self.db.get_session_context(self.session_id)
        # FIXME: copied cover from tracer, we might want to refactor
        nodes = self.db.get_nodes_for_session(self.session_id)
        return Graph(nodes, session_context)

    def to_airflow(self, filename: Optional[str] = None) -> Path:
        """
        Writes the airflow job to a path on disk.

        If a filename is not passed in, will write the dag to the airflow home.
        """
        # We have to look up the session based on the node, since
        # thats where we save the working directory.
        # TODO: Move into DB and make session a relation of node.
        node_orm = (
            self.db.session.query(BaseNodeORM)
            .filter(BaseNodeORM.id == self.node_id)
            .one()
        )
        session_orm = (
            self.db.session.query(SessionContextORM)
            .filter(SessionContextORM.id == node_orm.session_id)
            .one()
        )
        working_dir = Path(session_orm.working_directory)

        airflow_code = to_airflow(self.code, self.name, working_dir)
        if filename:
            path = Path(filename)
        else:
            # Save dag to dags folder in airflow home
            # Otherwise default to default airflow home in home directory
            path = (
                (
                    Path(environ["AIRFLOW_HOME"])
                    if "AIRFLOW_HOME" in environ
                    else Path.home() / "airflow"
                )
                / "dags"
                / f"{self.name}.py"
            )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(airflow_code)
        print(
            f"Added Airflow DAG named '{self.name}'. Start a run from the Airflow UI or CLI."
        )
        return path

    def visualize(self) -> None:
        """
        Displays the graph for this artifact.
        """
        from lineapy.visualizer import Visualizer

        display(
            Visualizer.for_public_node(
                self._graph, self.node_id
            ).ipython_display_object()
        )


class LineaCatalog:
    """LineaCatalog

    A simple way to access meta data about artifacts in Linea
    """

    """
    DEV NOTE:
    - The export is pretty limited right now and we should expand later.
    """

    db: RelationalLineaDB

    def __init__(self, db):
        self.db = db
        self.artifacts = self.db.get_all_artifacts()

    @cached_property
    def print(self) -> str:
        return "\n".join(
            [f"{a.name}, {a.date_created}" for a in self.artifacts]
        )

    def __str__(self) -> str:
        return self.print

    def __repr__(self) -> str:
        return self.print

    @cached_property
    def export(self):
        """
        Returns
        -------
            a dictionary of artifact information, which the user can then
            manipulate with their favorite dataframe tools, such as pandas,
            e.g., `cat_df = pd.DataFrame(catalog.export())`.
        """
        return [
            {"artifact_name": a.name, "date_created": a.date_created}
            for a in self.artifacts
        ]
