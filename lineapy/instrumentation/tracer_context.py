from dataclasses import dataclass
from typing import Dict, List

from lineapy.data.graph import Graph
from lineapy.data.types import LineaID, SessionContext
from lineapy.db.db import RelationalLineaDB
from lineapy.db.relational import ArtifactORM
from lineapy.graph_reader.program_slice import get_program_slice


@dataclass
class TracerContext:
    """
    This context will be used by tracer to store any data that is needed after the tracer has exited.
    This will hold reference to any internal dicts that are used outside the tracer and its session.
    """

    db: RelationalLineaDB
    session_context: SessionContext

    @classmethod
    def reload_session(
        cls, db: RelationalLineaDB, session_id: LineaID
    ) -> "TracerContext":
        session_context = db.get_session_context(session_id)
        return cls(db, session_context)

    def get_session_id(self) -> LineaID:
        return self.session_context.id

    @property
    def graph(self) -> Graph:
        """
        Creates a graph by fetching all the nodes about this session from the DB.
        """
        nodes = self.db.get_nodes_for_session(self.get_session_id())
        return Graph(nodes, self.session_context)

    def session_artifacts(self) -> List[ArtifactORM]:
        return self.db.get_artifacts_for_session(self.get_session_id())

    @property
    def artifacts(self) -> Dict[str, str]:
        """
        Returns a mapping of artifact names to their sliced code.
        """

        return {
            artifact.name: get_program_slice(self.graph, [artifact.node_id])
            for artifact in self.session_artifacts()
            if artifact.name is not None
        }

    def slice(self, name: str) -> str:
        artifact = self.db.get_artifact_by_name(name)
        return get_program_slice(self.graph, [artifact.node_id])
