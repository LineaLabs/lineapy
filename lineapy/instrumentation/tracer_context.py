from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Tuple

from lineapy.data.graph import Graph
from lineapy.data.types import LineaID, Node, SessionContext
from lineapy.db.db import RelationalLineaDB
from lineapy.db.relational import ArtifactORM
from lineapy.graph_reader.program_slice import get_program_slice
from lineapy.instrumentation.mutation_tracker import MutationTracker


@dataclass
class TracerContext:
    """
    This context will be used by tracer to store any data that is needed after the tracer has exited.
    This will hold reference to any internal dicts that are used outside the tracer and its session.
    """

    db: RelationalLineaDB
    session_context: SessionContext
    mutation_tracker: MutationTracker = field(default_factory=MutationTracker)
    variable_name_to_node: Dict[str, Node] = field(default_factory=dict)

    def __getattr__(self, __name: str) -> Any:
        mutation_tracker_method = getattr(self.mutation_tracker, __name, None)
        if mutation_tracker_method is not None:
            return mutation_tracker_method
        else:
            raise AttributeError(f"{__name} not found in TracerContext")

    def update_node_by_variable_name(
        self, variable_name: str, node: Node
    ) -> None:
        self.variable_name_to_node[variable_name] = node

    def get_nodes(self) -> Iterable[Tuple[str, Node]]:
        for k, n in self.variable_name_to_node.items():
            yield k, n

    def get_node_id_from_variable_name(self, variable_name: str) -> LineaID:
        return self.get_node_from_variable_name(variable_name).id

    def get_node_from_variable_name(self, variable_name: str) -> Node:
        return self.variable_name_to_node[variable_name]

    def get_filtered_mutated_nodes(self, retrieved: List[str]):
        return {
            var: self.mutation_tracker.get_latest_mutate_node(
                self.variable_name_to_node[var].id
            )
            for var in retrieved
            # Only save reads from variables that we have already saved variables for
            # Assume that all other reads are for variables assigned inside the call
            if var in self.variable_name_to_node
        }

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

    def slice(self, name: str) -> str:
        artifact = self.db.get_artifact_by_name(name)
        return get_program_slice(self.graph, [artifact.node_id])
