from __future__ import annotations

import builtins
import importlib.util
import logging
import operator
from dataclasses import dataclass, field
from datetime import datetime
from os import chdir, getcwd
from typing import (
    Callable,
    Dict,
    Hashable,
    Iterable,
    List,
    Optional,
    Tuple,
    cast,
)

from lineapy.data.graph import Graph
from lineapy.data.types import (
    CallNode,
    Execution,
    GlobalNode,
    ImportNode,
    LineaID,
    LiteralNode,
    LookupNode,
    MutateNode,
    Node,
)
from lineapy.db.db import RelationalLineaDB
from lineapy.editors.ipython_cell_storage import get_location_path
from lineapy.exceptions.db_exceptions import ArtifactSaveException
from lineapy.exceptions.user_exception import (
    AddFrame,
    RemoveFrames,
    RemoveFramesWhile,
    TracebackChange,
    UserException,
)
from lineapy.execution.context import set_context, teardown_context
from lineapy.execution.inspect_function import FunctionInspector
from lineapy.execution.side_effects import (
    ID,
    ExecutorPointer,
    ImplicitDependencyNode,
    MutatedNode,
    SideEffect,
    ViewOfNodes,
)
from lineapy.instrumentation.annotation_spec import (
    BoundSelfOfFunction,
    ExternalState,
    ImplicitDependencyValue,
    InspectFunctionSideEffect,
    KeywordArgument,
    MutatedValue,
    PositionalArg,
    Result,
    ValuePointer,
    ViewOfValues,
)
from lineapy.utils.lineabuiltins import LINEA_BUILTINS
from lineapy.utils.utils import get_new_id

try:
    from functools import singledispatchmethod  # type: ignore
except ImportError:  # pragma: no cover
    # this is the fallback for python < 3.8
    # https://stackoverflow.com/questions/24601722
    from lineapy.utils.deprecation_utils import (  # type: ignore
        singledispatchmethod,
    )


logger = logging.getLogger(__name__)


# Need to define first in file, even though private, since used as type param
# for single dispatch decorator and that requires typings to resolve
@dataclass
class PrivateExecuteResult:
    value: object
    start_time: datetime
    end_time: datetime
    side_effects: List[SideEffect]


@dataclass
class Executor:
    """
    An executor that is responsible for executing a graph, either node by
    node as it is created, or in a batch, after the fact.

    To use the executor, you first instantiate it. Then you can execute nodes, by calling
    `execute_node`. This returns a list of side effects that executing that node causes.

    You can also query for the time a node took to execute or its value, using `get_value` and `get_execution_time`.
    """

    # The database to use for saving the execution
    db: RelationalLineaDB

    # The globals for this execution, to use when trying to lookup a value
    # Note: This is set in Jupyter so that `get_ipython` is defined
    _globals: dict[str, object]

    # The __file__ for the module being executed
    # https://docs.python.org/3/reference/import.html#file__
    module_file: Optional[str] = None

    # The execution to record the values in
    # This is accessed via the ExecutionContext, which is set when executing a node
    # so that artifacts created during the execution know which execution they should refer to.
    execution: Execution = field(init=False)

    _function_inspector: FunctionInspector = field(
        default_factory=FunctionInspector
    )
    _id_to_value: dict[LineaID, object] = field(default_factory=dict)
    _execution_time: dict[LineaID, Tuple[datetime, datetime]] = field(
        default_factory=dict
    )
    # Mapping of bound method node ids to the ID of the instance they are bound to
    _node_to_bound_self: Dict[LineaID, LineaID] = field(default_factory=dict)

    # Mapping of call node to the values of the globals that were updated
    # Saved so that when we get these globals, we know their values
    # TODO: rename to variable
    _node_to_globals: Dict[LineaID, Dict[str, object]] = field(
        default_factory=dict
    )

    # Mapping of values to their nodes. Currently the only values
    # in here are external state values
    _value_to_node: Dict[Hashable, LineaID] = field(default_factory=dict)

    def __post_init__(self):
        self.execution = Execution(
            id=get_new_id(),
            timestamp=datetime.now(),
        )
        self.db.write_execution(self.execution)

    def get_execution_time(
        self, node_id: LineaID
    ) -> Tuple[datetime, datetime]:
        """
        Returns the (startime, endtime) for a node that was execute.

        Only applies for function call nodes.
        """
        return self._execution_time[node_id]

    def get_value(self, node_id: LineaID) -> object:
        """
        Gets the Python in memory value for a node which was already executed.
        """
        return self._id_to_value[node_id]

    def execute_node(
        self, node: Node, variables: Optional[Dict[str, LineaID]] = None
    ) -> Iterable[SideEffect]:
        """
        Variables is the mapping from local variable names to their nodes. It
        is passed in on the first execution, but on re-executions it is empty.

        At that point we know which variables each call node depends on, since
        the first time we executed we captured that.

        Does the following:

        - Executes a node
        - And records

          - value (currently: only for call nodes and all call nodes)
          - execution time

        - Add a new frame to the stack to support error reporting. Without it,
          the traceback will be empty.
        - Returns the `SideEffects` of this node that's analyzed at runtime (hence in the executor).
        """
        logger.debug("Executing node %s", node)

        # To use if we need to raise an exception and change the frame
        default_changes: List[AddFrame] = []
        # If we know the source location, add that frame at the top
        if node.source_location:
            location = node.source_location.source_code.location
            default_changes.append(
                AddFrame(
                    str(get_location_path(location).absolute()),
                    node.source_location.lineno,
                )
            )

        res = self._execute(node, default_changes, variables)
        value = res.value
        self._id_to_value[node.id] = value
        self._execution_time[node.id] = res.start_time, res.end_time
        # If this is some external state node, save it by its value,
        # so we can look it up later if we try access it
        if isinstance(value, ExternalState):
            # If we already know about this node, add an implicit
            # dependency from the old version to the new one

            if value in self._value_to_node:
                # However, don't add any edges for mutate nodes, since
                # they already should have it from the source
                if not isinstance(node, MutateNode):
                    res.side_effects.append(
                        ImplicitDependencyNode(ID(self._value_to_node[value]))
                    )
                # If this is a mutate node, then update the value to node to the new
                # value, so we always get the last one
                else:
                    self._value_to_node[value] = node.id

            # Otherwise, this is the first time we are seeing it, so
            # add it to our lookup
            else:
                self._value_to_node[value] = node.id
        return res.side_effects

    @singledispatchmethod
    def _execute(
        self,
        node: Node,
        changes: Iterable[TracebackChange],
        variables: Optional[Dict[str, LineaID]],
    ) -> PrivateExecuteResult:
        """
        Executes a node, returning the resulting value, the start and end times,
        and any side effects
        """
        raise NotImplementedError(
            f"Don't know how to execute node type {type(node)}"
        )

    @_execute.register
    def _execute_lookup(
        self,
        node: LookupNode,
        changes: Iterable[TracebackChange],
        variables: Optional[Dict[str, LineaID]],
    ) -> PrivateExecuteResult:
        # If we get a lookup error, change it to a name error to match python
        try:
            start_time = datetime.now()
            value = self._lookup_value(node.name)
            end_time = datetime.now()
        except KeyError:
            # Matches Python's message---our execution causes a KeyError,
            # but for the same user code, vanilla Python would throw NameError
            # which is why we needed to change the error type.
            message = f"name '{node.name}' is not defined"
            raise UserException(NameError(message), *changes)
        return PrivateExecuteResult(value, start_time, end_time, [])

    @_execute.register
    def _execute_call(
        self,
        node: CallNode,
        changes: Iterable[TracebackChange],
        variables: Optional[Dict[str, LineaID]],
    ) -> PrivateExecuteResult:

        fn = cast(Callable, self._id_to_value[node.function_id])

        # If we are getting an attribute, save the value in case
        # we later call it as a bound method and need to track its mutations
        # For example, for `a = [1]; a.append(2)`
        # We need to trace `a`, as opposed to `a.append` when tracking the
        # mutation.
        if fn is getattr:
            self._node_to_bound_self[node.id] = node.positional_args[0].id

        args: List[object] = []
        for p_arg in node.positional_args:
            if p_arg.starred:
                args.extend(cast(Iterable, self._id_to_value[p_arg.id]))
            else:
                args.append(self._id_to_value[p_arg.id])
        kwargs = {}
        for k in node.keyword_args:
            if k.starred:
                kwargs.update(cast(Dict, self._id_to_value[k.value]))
            else:
                kwargs.update({k.key: self._id_to_value[k.value]})

        logger.debug("Calling function %s %s %s", fn, args, kwargs)

        # Set up our execution context, with our globals and node
        set_context(self, variables, node)

        try:
            start_time = datetime.now()
            res = fn(*args, **kwargs)
            end_time = datetime.now()
        except ArtifactSaveException:
            # keep the error stack if its artifact save
            raise
        except Exception as exc:
            # this is user error, so use the custom exception so we can clean
            # up our call stack
            raise UserException(exc, RemoveFrames(1), *changes)
        finally:
            logger.debug("Tearing down context")
            # Check what has been changed and accessed in the globals
            # Do this in a finally, so its always torn down even after exceptions
            globals_result = teardown_context()

        self._node_to_globals[node.id] = globals_result.added_or_modified

        """
        Add all side effects from context as well as side effects from 
           inspecting function.
        `side_effects` is an iterable, so that each translated 
          side effect is resolved after the previous one has been executed 
          (the control is yielded). Consider 
          ```
          with open("...", "w") as f
          ```
          We create both the node that represents the side-effect, and a view node
          so the side-effect from the inspect_function in the executor, if the 
          executor sees that there is no node (first time), then sends to tracer,
          tracer creates a lookup node, then give back to executor to process it.

        NOTE: we have a near term eng goal to refactor how side-effect is
              handled.
        """
        logger.debug("Resolving side effects")
        side_effects = globals_result.side_effects + [
            self._translate_side_effect(node, e)
            for e in self._function_inspector.inspect(fn, args, kwargs, res)
        ]

        return PrivateExecuteResult(res, start_time, end_time, side_effects)

    def lookup_external_state(self, state: ExternalState) -> Optional[LineaID]:
        """
        Returns the node ID if we have created a node already for some external state.

        Otherwise, returns None.
        """
        return self._value_to_node.get(state, None)

    @_execute.register
    def _execute_import(
        self,
        node: ImportNode,
        changes: Iterable[TracebackChange],
        variables: Optional[Dict[str, LineaID]],
    ) -> PrivateExecuteResult:
        try:
            start_time = datetime.now()
            value = importlib.import_module(node.name)
            end_time = datetime.now()
        except Exception as exc:
            # Remove all importlib frames
            # There are a different number depending on whether the import
            # can be resolved
            filter = RemoveFramesWhile(
                lambda frame: frame.f_code.co_filename.startswith(
                    "<frozen importlib"
                )
            )
            raise UserException(
                exc,
                # Remove the first two frames, which are always there
                RemoveFrames(2),
                # Then filter all frozen importlib frames
                filter,
                *changes,
            )
        return PrivateExecuteResult(value, start_time, end_time, [])

    @_execute.register
    def _execute_literal(
        self,
        node: LiteralNode,
        changes: Iterable[TracebackChange],
        variables: Optional[Dict[str, LineaID]],
    ) -> PrivateExecuteResult:
        return PrivateExecuteResult(
            node.value, datetime.now(), datetime.now(), []
        )

    @_execute.register
    def _execute_global(
        self,
        node: GlobalNode,
        changes: Iterable[TracebackChange],
        variables: Optional[Dict[str, LineaID]],
    ) -> PrivateExecuteResult:
        return PrivateExecuteResult(
            # An execute global is looking up a global set by a call node so,
            # Copy the result and the timing from the call node
            self._node_to_globals[node.call_id][node.name],
            *self._execution_time[node.call_id],
            [],
        )

    @_execute.register
    def _execute_mutate(
        self,
        node: MutateNode,
        changes: Iterable[TracebackChange],
        variables: Optional[Dict[str, LineaID]],
    ) -> PrivateExecuteResult:
        return PrivateExecuteResult(
            # Copy the result and the timing from the source node
            self._id_to_value[node.source_id],
            *self._execution_time[node.call_id],
            [ViewOfNodes([ID(node.id), ID(node.source_id)])],
        )

    def execute_graph(self, graph: Graph) -> None:
        """
        Executes a graph in visit order making sure to setup the working directory first.

        TODO: Possibly move to graph instead of on executor, since it rather cleanly uses the
        executor's public API? Or move to function?
        """
        logger.debug("Executing graph %s", graph)
        prev_working_dir = getcwd()
        chdir(graph.session_context.working_directory)
        for node in graph.visit_order():
            self.execute_node(node, variables=None)
        chdir(prev_working_dir)
        # Add executed nodes to DB
        self.db.session.commit()

    def _translate_pointer(
        self, node: CallNode, pointer: ValuePointer
    ) -> ExecutorPointer:
        """
        Maps from a pointer output by the inspect function, to one output by the executor.
        """
        if isinstance(pointer, PositionalArg):
            return ID(
                node.positional_args[pointer.positional_argument_index].id
            )
        elif isinstance(pointer, KeywordArgument):
            # these come from annotation specs so should not need to worry about ** dicts
            for k in node.keyword_args:
                if k.key == pointer.argument_keyword:
                    return ID(k.value)
        elif isinstance(pointer, Result):
            return ID(node.id)
        elif isinstance(pointer, BoundSelfOfFunction):
            return ID(self._node_to_bound_self[node.function_id])
        elif isinstance(pointer, ExternalState):
            return pointer
        raise ValueError(f"Unknown pointer {pointer}, of type {type(pointer)}")

    def _translate_side_effect(
        self, node: CallNode, e: InspectFunctionSideEffect
    ) -> SideEffect:
        if isinstance(e, MutatedValue):
            return MutatedNode(self._translate_pointer(node, e.mutated_value))
        elif isinstance(e, ImplicitDependencyValue):
            return ImplicitDependencyNode(
                self._translate_pointer(node, e.dependency)
            )
        elif isinstance(e, ViewOfValues):
            return ViewOfNodes(
                [self._translate_pointer(node, ptr) for ptr in e.views]
            )
        raise NotImplementedError(
            f"Unknown side effect {e}, of type {type(e)}"
        )

    def _lookup_value(self, name: str) -> object:
        """
        Lookup a value from a string identifier.
        """
        if name == "__file__":
            if self.module_file:
                return self.module_file
            raise ValueError("No __file__ set")
        if hasattr(builtins, name):
            return getattr(builtins, name)
        if hasattr(operator, name):
            return getattr(operator, name)
        if name in LINEA_BUILTINS:
            return LINEA_BUILTINS[name]
        return self._globals[name]
