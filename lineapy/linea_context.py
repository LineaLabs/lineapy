from dataclasses import InitVar, dataclass, field
from datetime import datetime
from os import getcwd
from typing import Dict, List, Optional, Union, cast

from IPython.display import DisplayObject

from lineapy.data.graph import Graph
from lineapy.data.types import SessionContext, SessionType
from lineapy.db.db import RelationalLineaDB
from lineapy.db.relational import ArtifactORM
from lineapy.db.utils import MEMORY_DB_URL
from lineapy.editors.states import CellsExecutedState, StartedState
from lineapy.execution.context import ExecutionContext
from lineapy.execution.executor import Executor
from lineapy.global_context import IPYTHON_EVENTS, TRACER_EVENTS, GlobalContext
from lineapy.graph_reader.program_slice import get_program_slice
from lineapy.instrumentation.mutation_tracker import MutationTracker
from lineapy.instrumentation.tracer import Tracer
from lineapy.utils.utils import get_new_id


@dataclass
class LineaGlobalContext(GlobalContext):
    db: RelationalLineaDB = field(init=False)
    session_context: SessionContext = field(init=False)
    session_name: InitVar[Optional[str]] = None
    globals_: InitVar[Optional[Dict[str, object]]] = None

    IPYSTATE: Union[None, StartedState, CellsExecutedState] = None
    execution_context: Optional[ExecutionContext] = None
    executor: Executor = field(init=False)
    mutation_tracker: MutationTracker = field(default_factory=MutationTracker)
    tracer: Tracer = field(init=False)

    def __post_init__(
        self,
        session_type: SessionType,
        session_name: Optional[str],
        globals_: Optional[Dict[str, object]],
    ):
        self.session_type = session_type
        if session_type == SessionType.JUPYTER and self.IPYSTATE is None:
            return
        if (
            not hasattr(LineaGlobalContext, "db")
            and session_type != SessionType.JUPYTER
        ):
            LineaGlobalContext.db = RelationalLineaDB.from_environment(
                MEMORY_DB_URL
            )
        if session_type != SessionType.JUPYTER or not hasattr(
            LineaGlobalContext, "executor"
        ):
            LineaGlobalContext.executor = Executor(
                LineaGlobalContext.db, globals()
            )
            GlobalContext.variable_name_to_node = {}
        LineaGlobalContext.session_context = SessionContext(
            id=get_new_id(),
            environment_type=session_type,
            creation_time=datetime.now(),
            working_directory=getcwd(),
            session_name="test",
            execution_id=LineaGlobalContext.executor.execution.id,
        )
        LineaGlobalContext.db.write_context(LineaGlobalContext.session_context)
        tracer = Tracer()
        tracer._context_manager = self
        LineaGlobalContext.tracer = tracer

    @classmethod
    def discard_existing_and_create_new_session(
        cls, session_type, globals_=None
    ) -> "LineaGlobalContext":
        return cls(session_type, globals_)

    @classmethod
    @property
    def graph(self) -> Graph:
        """
        Creates a graph by fetching all the nodes about this session from the DB.
        """
        nodes = LineaGlobalContext.db.get_nodes_for_session(
            self.session_context.id
        )
        return Graph(nodes, self.session_context)

    @property
    def values(self) -> Dict[str, object]:
        """
        Returns a mapping of variable names to their values, by joining
        the scoping information with the executor values.
        """
        return {
            k: self.executor.get_value(n.id)
            for k, n in self.variable_name_to_node.items()
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

    @classmethod
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

    @classmethod
    def session_artifacts(self) -> List[ArtifactORM]:
        return self.db.get_artifacts_for_session(self.session_context.id)

    @classmethod
    def slice(self, name: str) -> str:
        artifact = LineaGlobalContext.db.get_artifact_by_name(name)
        return get_program_slice(
            # dunno why i need to do this yet
            cast(Graph, LineaGlobalContext.graph),
            [artifact.node_id],
        )

    def create_visualize_display_object(self) -> DisplayObject:
        """
        Returns a jupyter display object for the visualization.
        """
        from lineapy.visualizer import Visualizer

        return Visualizer.for_public(self).ipython_display_object()

    def notify(
        self,
        operator: object,
        event: Union[None, TRACER_EVENTS, IPYTHON_EVENTS],
        *args,
        **kwargs
    ) -> None:
        """
        Notifies the context that a node has been executed.
        """
        if event == IPYTHON_EVENTS.StartedState:
            # TODO do all the db init etc here
            if self.IPYSTATE is None:
                self.session_name = kwargs.get("session_name")
                self.IPYSTATE = StartedState(*args, **kwargs)
                LineaGlobalContext.db = RelationalLineaDB.from_environment(
                    self.IPYSTATE.db_url
                )
                # LineaGlobalContext.executor = Executor(
                #     LineaGlobalContext.db, globals()
                # )
                # GlobalContext.variable_name_to_node = {}
        if event == IPYTHON_EVENTS.CellsExecutedState:
            _globals = kwargs["globals"]
            LineaGlobalContext.executor = Executor(
                LineaGlobalContext.db, _globals
            )
            GlobalContext.variable_name_to_node = {}
            LineaGlobalContext.session_context = SessionContext(
                id=get_new_id(),
                environment_type=self.session_type,
                creation_time=datetime.now(),
                working_directory=getcwd(),
                session_name=self.session_name,
                execution_id=LineaGlobalContext.executor.execution.id,
            )
            LineaGlobalContext.db.write_context(
                LineaGlobalContext.session_context
            )
            tracer = Tracer()
            tracer._context_manager = self
            LineaGlobalContext.tracer = tracer
            self.IPYSTATE = CellsExecutedState(code=kwargs["code"])
