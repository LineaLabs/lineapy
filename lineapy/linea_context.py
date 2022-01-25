import ast
import sys
from dataclasses import InitVar, dataclass, field
from datetime import datetime
from os import getcwd
from typing import Dict, List, Optional, Union, cast

from IPython.display import DisplayObject

from lineapy.data.graph import Graph
from lineapy.data.types import (
    Node,
    SessionContext,
    SessionType,
    SourceCodeLocation,
)
from lineapy.db.db import RelationalLineaDB
from lineapy.db.relational import ArtifactORM
from lineapy.db.utils import MEMORY_DB_URL
from lineapy.editors.ipython_cell_storage import get_location_path
from lineapy.editors.states import CellsExecutedState, StartedState
from lineapy.exceptions.user_exception import RemoveFrames, UserException
from lineapy.execution.context import ExecutionContext
from lineapy.execution.executor import Executor
from lineapy.global_context import IPYTHON_EVENTS, TRACER_EVENTS, GlobalContext
from lineapy.graph_reader.program_slice import get_program_slice
from lineapy.instrumentation.mutation_tracker import MutationTracker
from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.node_transformer import NodeTransformer
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
    node_transformer: NodeTransformer = field(init=False)

    def __post_init__(
        self,
        session_type: SessionType,
        session_name: Optional[str],
        globals_: Optional[Dict[str, object]],
    ):
        self.session_type = session_type
        if session_type == SessionType.JUPYTER and self.IPYSTATE is None:
            return
        if not hasattr(self, "db") and session_type != SessionType.JUPYTER:
            self.db = RelationalLineaDB.from_environment(MEMORY_DB_URL)
        if session_type != SessionType.JUPYTER or not hasattr(
            self, "executor"
        ):
            self.executor = Executor(self.db, globals())
            GlobalContext.variable_name_to_node = {}
        self.session_context = SessionContext(
            id=get_new_id(),
            environment_type=session_type,
            creation_time=datetime.now(),
            working_directory=getcwd(),
            session_name="test",
            execution_id=self.executor.execution.id,
        )
        self.db.write_context(self.session_context)
        tracer = Tracer()
        tracer._context_manager = self
        self.tracer = tracer

    @classmethod
    def discard_existing_and_create_new_session(
        cls, session_type, globals_=None
    ) -> "LineaGlobalContext":
        return cls(session_type, globals_)

    @property
    def graph(self) -> Graph:
        """
        Creates a graph by fetching all the nodes about this session from the DB.
        """
        nodes = self.db.get_nodes_for_session(self.session_context.id)
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
            # dunno why i need to do this yet
            cast(Graph, self.graph),
            [artifact.node_id],
        )

    def transform(
        self, code: str, location: SourceCodeLocation
    ) -> Optional[Node]:
        """
        Traces the given code, executing it and writing the results to the DB.

        It returns the node corresponding to the last statement in the code,
        if it exists.
        """

        node_transformer = NodeTransformer()
        node_transformer.context_manager = self
        node_transformer.set_context(code, location, self.tracer)
        self.node_transformer = node_transformer
        try:
            tree = ast.parse(
                code,
                str(get_location_path(location).absolute()),
            )
        except SyntaxError as e:
            raise UserException(e, RemoveFrames(2))
        if sys.version_info < (3, 8):
            from asttokens import ASTTokens

            from lineapy.transformer.source_giver import SourceGiver

            # if python version is 3.7 or below, we need to run the source_giver
            # to add the end_lineno's to the nodes. We do this in two steps - first
            # the asttoken lib does its thing and adds tokens to the nodes
            # and then we swoop in and copy the end_lineno from the tokens
            # and claim credit for their hard work
            ASTTokens(code, parse=False, tree=tree)
            SourceGiver().transform(tree)

        node_transformer.visit(tree)

        self.db.commit()
        return node_transformer.last_statement_result

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
                self.db = RelationalLineaDB.from_environment(
                    self.IPYSTATE.db_url
                )
                # LineaGlobalContext.executor = Executor(
                #     LineaGlobalContext.db, globals()
                # )
                # GlobalContext.variable_name_to_node = {}
        if event == IPYTHON_EVENTS.CellsExecutedState:
            _globals = kwargs["globals"]
            self.executor = Executor(self.db, _globals)
            self.variable_name_to_node = {}
            self.session_context = SessionContext(
                id=get_new_id(),
                environment_type=self.session_type,
                creation_time=datetime.now(),
                working_directory=getcwd(),
                session_name=self.session_name,
                execution_id=self.executor.execution.id,
            )
            self.db.write_context(self.session_context)
            tracer = Tracer()
            tracer._context_manager = self
            self.tracer = tracer
            self.IPYSTATE = CellsExecutedState(code=kwargs["code"])
