from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import Dict, List, Union, cast

from lineapy.data.graph import Graph
from lineapy.data.types import Node, SessionContext, SessionType
from lineapy.db.db import RelationalLineaDB
from lineapy.db.relational import ArtifactORM
from lineapy.graph_reader.program_slice import get_program_slice


class TRACER_EVENTS(Enum):
    CALL = "CALL"
    TRACEIMPORT = "TIMPORT"
    VISUALIZE = "visualize"


class IPYTHON_EVENTS(Enum):
    StartedState = "StartedState"
    CellsExecutedState = "CellsExecutedState"


class GlobalContext(ABC):
    session_type: SessionType
    db: RelationalLineaDB
    session_context: SessionContext
    variable_name_to_node: Dict[str, Node]

    def __init__(self, session_type, db):
        self.session_type = session_type
        self.db = db
        self.variable_name_to_node = {}

    def notify(
        self,
        operator: object,
        event: Union[None, TRACER_EVENTS, IPYTHON_EVENTS],
        *args,
        **kwargs
    ) -> None:
        pass

    @property
    def graph(self) -> Graph:
        """
        Creates a graph by fetching all the nodes about this session from the DB.
        """
        nodes = self.db.get_nodes_for_session(self.session_context.id)
        return Graph(nodes, self.session_context)

    @property
    def values(self) -> Dict[str, object]:
        pass

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

    def artifact_var_name(self, artifact_name: str) -> str:
        """
        Returns the variable name for the given artifact.
        i.e. in lineapy.save(p, "p value") "p" is returned
        """
        artifact = self.db.get_artifact_by_name(artifact_name)
        if not artifact.node or not artifact.node.source_code:
            return ""
        _line_no = artifact.node.lineno if artifact.node.lineno else 0
        artifact_line = str(artifact.node.source_code.code).split("\n")[
            _line_no - 1
        ]
        _col_offset = (
            artifact.node.col_offset if artifact.node.col_offset else 0
        )
        if _col_offset < 3:
            return ""
        return artifact_line[: _col_offset - 3]

    def session_artifacts(self) -> List[ArtifactORM]:
        return self.db.get_artifacts_for_session(self.session_context.id)

    def slice(self, name: str) -> str:
        artifact = self.db.get_artifact_by_name(name)
        return get_program_slice(
            # dunno why i need to do this yetx
            self.graph,
            [artifact.node_id],
        )
