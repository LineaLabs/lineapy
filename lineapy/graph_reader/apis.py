from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Any, Optional

from lineapy.data.graph import Graph
from lineapy.data.types import LineaID, SessionContext
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.db.relational.schema.relational import NodeValueORM
from lineapy.graph_reader.program_slice import get_program_slice

"""
User exposed APIs.
Should keep it very clean.
"""


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

    def __init__(
        self,
        db: RelationalLineaDB,
        node_id: LineaID,
    ):
        self.db: RelationalLineaDB = db
        self._node_id = node_id
        session_id = db.get_node_by_id(node_id).session_id

        self._session_context: SessionContext = self.db.get_session_context(
            session_id
        )

        # FIXME: copied cover from tracer, we might want to refactor
        nodes = self.db.get_nodes_for_session(session_id)
        graph = Graph(nodes, self._session_context)
        # FIXME: this seems a little heavy to just get the slice?
        self.code = get_program_slice(graph, [node_id])

    @classmethod
    def from_artifact_name(
        cls, artifact_name: str, db: RelationalLineaDB
    ) -> LineaArtifact:
        artifact = db.get_artifact_by_name(artifact_name)
        return cls(db, artifact)

    @cached_property
    def _node_value_orm(self) -> Optional[NodeValueORM]:
        return self.db.get_node_value_from_db(
            self._node_id, self._session_context.execution_id
        )

    @cached_property
    def value(self) -> Any:
        # FIXME: the versioning semantics here is kinda weird
        #        the execution_id I believe is redundant right now
        if self._node_value_orm is not None:
            return self._node_value_orm.value
        else:
            return None


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
