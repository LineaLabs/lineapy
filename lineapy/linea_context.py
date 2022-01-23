from dataclasses import InitVar, dataclass, field
from datetime import datetime
from os import getcwd
from typing import Dict, List, Optional, Union

from lineapy.data.graph import Graph
from lineapy.data.types import Node, SessionContext, SessionType
from lineapy.db.db import RelationalLineaDB
from lineapy.db.relational import ArtifactORM
from lineapy.db.utils import MEMORY_DB_URL
from lineapy.editors.states import CellsExecutedState, StartedState
from lineapy.execution.context import ExecutionContext
from lineapy.execution.executor import Executor
from lineapy.graph_reader.program_slice import get_program_slice
from lineapy.instrumentation.mutation_tracker import MutationTracker
from lineapy.utils.utils import get_new_id


@dataclass
class LineaGlobalContext:
    db: RelationalLineaDB = field(init=False)
    session_context: SessionContext = field(init=False)
    session_type: InitVar[SessionType]
    session_name: InitVar[Optional[str]] = None

    STATE: Union[None, StartedState, CellsExecutedState] = None
    execution_context: Optional[ExecutionContext] = None
    executor: Executor = field(init=False)
    mutation_tracker: MutationTracker = field(default_factory=MutationTracker)
    variable_name_to_node: Dict[str, Node] = field(default_factory=dict)

    def __post_init__(
        self,
        session_type: SessionType,
        session_name: Optional[str],
    ):
        if not hasattr(LineaGlobalContext, "db"):
            LineaGlobalContext.db = RelationalLineaDB.from_environment(
                MEMORY_DB_URL
            )
            LineaGlobalContext.executor = Executor(
                LineaGlobalContext.db, globals()
            )
            LineaGlobalContext.variable_name_to_node = {}
        LineaGlobalContext.session_context = SessionContext(
            id=get_new_id(),
            environment_type=session_type,
            creation_time=datetime.now(),
            working_directory=getcwd(),
            session_name=session_name,
            execution_id=self.executor.execution.id,
        )
        LineaGlobalContext.db.write_context(LineaGlobalContext.session_context)

    @classmethod
    def discard_existing_and_create_new_session(
        cls, session_type
    ) -> "LineaGlobalContext":
        return cls(session_type)

    @property
    def graph(self) -> Graph:
        """
        Creates a graph by fetching all the nodes about this session from the DB.
        """
        nodes = LineaGlobalContext.db.get_nodes_for_session(
            self.session_context.id
        )
        return Graph(nodes, self.session_context)

    @classmethod
    @property
    def values(cls) -> Dict[str, object]:
        """
        Returns a mapping of variable names to their values, by joining
        the scoping information with the executor values.
        """
        return {
            k: LineaGlobalContext.executor.get_value(n.id)
            for k, n in LineaGlobalContext.variable_name_to_node.items()
        }

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
        artifact = LineaGlobalContext.db.get_artifact_by_name(artifact_name)
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
        artifact = LineaGlobalContext.db.get_artifact_by_name(name)
        return get_program_slice(self.graph, [artifact.node_id])