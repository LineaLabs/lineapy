import ast
import sys
from datetime import datetime
from os import getcwd
from typing import Dict, Optional, Union

from IPython.display import DisplayObject

from lineapy.data.types import (
    Node,
    SessionContext,
    SessionType,
    SourceCodeLocation,
)
from lineapy.db.db import RelationalLineaDB

# from lineapy.db.utils import MEMORY_DB_URL
from lineapy.editors.ipython_cell_storage import get_location_path
from lineapy.editors.states import CellsExecutedState, StartedState
from lineapy.exceptions.user_exception import RemoveFrames, UserException
from lineapy.execution.executor import Executor
from lineapy.global_context import IPYTHON_EVENTS, TRACER_EVENTS, GlobalContext
from lineapy.instrumentation.mutation_tracker import MutationTracker
from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.node_transformer import NodeTransformer
from lineapy.utils.utils import get_new_id


class LineaGlobalContext(GlobalContext):
    session_name: Optional[str]
    globals_: Optional[Dict[str, object]]

    IPYSTATE: Union[None, StartedState, CellsExecutedState] = None
    executor: Executor
    mutation_tracker: MutationTracker = MutationTracker()
    tracer: Tracer
    node_transformer: NodeTransformer

    def __init__(
        self,
        session_type: SessionType,
        db: RelationalLineaDB,
        session_name: Optional[str],
    ):
        super().__init__(session_type, db)
        # self.session_type = session_type
        self.session_name = session_name
        if session_type == SessionType.JUPYTER and self.IPYSTATE is None:
            return
        self.db = db
        self._add_new_executor()
        self._create_new_session()
        self._add_new_tracer()

    def _add_new_tracer(self) -> None:
        """
        Associates a new tracer with the current context.
        """
        tracer = Tracer(self)
        self.tracer = tracer

    def _add_new_executor(self, **exoptions) -> None:
        """
        Associates a new executor with the current context.
        """
        __globals = exoptions.get("globals", globals())
        executor = Executor(self, __globals)
        self.executor = executor

    @classmethod
    def create_new_context(
        cls, session_type: SessionType, session_name: Optional[str] = None
    ) -> "LineaGlobalContext":
        # FIXME - this shouldnt be memory url - read from env by default
        db = RelationalLineaDB.from_environment(None)
        return cls(session_type, db, session_name)

    @classmethod
    def create_new_context_with_db(
        cls,
        session_type: SessionType,
        db: RelationalLineaDB,
        session_name: Optional[str] = None,
    ) -> "LineaGlobalContext":
        return cls(session_type, db, session_name)

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
        if event == IPYTHON_EVENTS.CellsExecutedState:
            _globals = kwargs.get("globals", None)
            self._add_new_executor(globals=_globals)
            self._create_new_session()
            self._add_new_tracer()
            self.IPYSTATE = CellsExecutedState(code=kwargs["code"])

    def _create_new_session(self):
        self.session_context = SessionContext(
            id=get_new_id(),
            environment_type=self.session_type,
            creation_time=datetime.now(),
            working_directory=getcwd(),
            session_name=self.session_name,
            execution_id=self.executor.execution.id,
        )
        self.db.write_context(self.session_context)
