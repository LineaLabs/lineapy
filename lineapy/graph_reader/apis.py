from functools import cached_property
from typing import Any, List, Optional

from lineapy.data.graph import Graph
from lineapy.data.types import Artifact, LineaID, Node, SessionContext
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.db.relational.schema.relational import ArtifactORM, NodeValueORM
from lineapy.graph_reader.program_slice import get_program_slice

"""
User exposed APIs.
Should keep it very clean.
"""


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

    db: RelationalLineaDB
    artifact_name: str

    def __init__(self, artifact_name: str, db: RelationalLineaDB):
        self.db = db
        self.artifact_name = artifact_name

    @cached_property
    def _artifact(self) -> ArtifactORM:
        """
        "private" because the user should not know what "Artifact" in our
        graph is.
        NOTE: a little messy mixing ORM types in here...
        """
        return self.db.get_artifact_by_name(self.artifact_name)

    # NOTE: assumes that all artifacts are callnodes
    @cached_property
    def _node(self) -> Node:
        return self.db.get_node_by_id(self._artifact.id)

    @cached_property
    def _session_id(self) -> LineaID:
        return self._node.session_id

    @cached_property
    def _session_context(self) -> SessionContext:
        return self.db.get_session_context(self._session_id)

    @cached_property
    def _graph(self) -> Graph:
        """
        FIXME: copied cover from tracer, we might want to refactor
        """
        nodes = self.db.get_nodes_for_session(self._session_id)
        return Graph(nodes, self._session_context)

    @cached_property
    def code(self) -> str:
        """
        FIXME: this seems a little heavy to just get the slice?
        """
        return get_program_slice(self._graph, [self._artifact.id])

    @cached_property
    def _node_value_orm(self) -> Optional[NodeValueORM]:
        return self.db.get_node_value_from_db(
            self._artifact.id, self._session_context.execution_id
        )

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

    @cached_property
    def _artifacts(self) -> List[Artifact]:
        # queries the DB
        return self.db.get_all_artifacts()

    @cached_property
    def print(self) -> str:
        return "\n".join(
            [f"{a.name}, {a.date_created}" for a in self._artifacts]
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
            for a in self._artifacts
        ]
