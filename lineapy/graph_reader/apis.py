"""
User exposed APIs.
Should keep it very clean.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property

from lineapy.data.graph import Graph
from lineapy.data.types import LineaID
from lineapy.db.db import RelationalLineaDB
from lineapy.graph_reader.program_slice import get_program_slice


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
        session_context = self.db.get_session_context(self.session_id)
        # FIXME: copied cover from tracer, we might want to refactor
        nodes = self.db.get_nodes_for_session(self.session_id)
        graph = Graph(nodes, session_context)
        # FIXME: this seems a little heavy to just get the slice?
        return get_program_slice(graph, [self.node_id])


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
