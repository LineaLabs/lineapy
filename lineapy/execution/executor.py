from __future__ import annotations

import builtins
import importlib.util
import logging
import operator
from dataclasses import dataclass, field
from datetime import datetime
from functools import singledispatchmethod
from os import chdir, getcwd
from typing import (
    Callable,
    Dict,
    Hashable,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
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
from lineapy.exceptions.db_exceptions import ArtifactSaveException
from lineapy.exceptions.user_exception import (
    AddFrame,
    RemoveFrames,
    RemoveFramesWhile,
    TracebackChange,
    UserException,
)
from lineapy.execution.context import set_context, teardown_context
from lineapy.execution.inspect_function import inspect_function, is_mutable
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
from lineapy.ipython_cell_storage import get_location_path
from lineapy.lineabuiltins import LINEA_BUILTINS
from lineapy.utils import get_new_id

logger = logging.getLogger(__name__)


# Need to define first in file, even though private, since used as type param
# for single dispatch decorator and that requires typings to resolve
@dataclass
class PrivateExecuteResult:
    value: object
    start_time: datetime
    end_time: datetime
    side_effects: SideEffects


@dataclass
class Executor:
    """
    An executor that is responsible for executing a graph, either node by
    node as it is created, or in a batch, after the fact.
    """

    # The database to use for saving the execution
    db: RelationalLineaDB
    # The execution to record the values in
    execution: Execution = field(init=False)

    # The globals for this execution, to use when trying to lookup a value
    # Note: This is set in Jupyter so that `get_ipython` is defined
    _globals: Dict[str, object]
    _id_to_value: Dict[LineaID, object] = field(default_factory=dict)
    _execution_time: Dict[LineaID, Tuple[datetime, datetime]] = field(
        default_factory=dict
    )
    # Mapping of bound method node ids to the ID of the instance they are bound to
    _node_to_bound_self: Dict[LineaID, LineaID] = field(default_factory=dict)

    # Mapping of call node to the globals that were updated
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
        Returns the (startime, endtime), only applies for function call nodes.
        """
        return self._execution_time[node_id]

    def get_value(self, node: Node) -> object:
        return self._id_to_value[node.id]

    def execute_node(
        self, node: Node, variables: Optional[Dict[str, LineaID]]
    ) -> SideEffects:
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
            value = self.lookup_value(node.name)
            end_time = datetime.now()
        except KeyError:
            # Matches Python's message
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

        # execute the function
        # ----------
        fn = cast(Callable, self._id_to_value[node.function_id])

        # If we are getting an attribute, save the value in case
        # we later call it as a bound method and need to track its mutations
        if fn is getattr:
            self._node_to_bound_self[node.id] = node.positional_args[0]

        args = [self._id_to_value[arg_id] for arg_id in node.positional_args]
        kwargs = {
            k: self._id_to_value[arg_id]
            for k, arg_id in node.keyword_args.items()
        }
        logger.debug("Calling function %s %s %s", fn, args, kwargs)

        # Set up our execution context, with our globals and node
        set_context(self, variables, node)

        try:
            start_time = datetime.now()
            res = fn(*args, **kwargs)
            end_time = datetime.now()
        # have to do this to avoid entering the general exception block below
        except ArtifactSaveException:
            raise
        except Exception as exc:
            raise UserException(exc, RemoveFrames(1), *changes)
        finally:
            # Check what has been changed and accessed in the globals
            # Do this in a finally, so its always torn down even after exceptions
            globals_result = teardown_context()

        self._node_to_globals[node.id] = globals_result.added_or_modified

        # dependency analysis
        # ----------

        # Any nodes that we retrieved that were mutable, assume were mutated
        # Filter the vars by if the value is mutable
        mutable_input_vars: List[ExecutorPointer] = [
            ID(id_)
            for id_ in globals_result.accessed_inputs.values()
            if is_mutable(self._id_to_value[id_])
        ]
        side_effects: SideEffects = [
            AccessedGlobals(
                list(globals_result.accessed_inputs.keys()),
                list(globals_result.added_or_modified.keys()),
            )
        ]

        side_effects.extend(map(MutatedNode, mutable_input_vars))

        # Now we mark all the mutable input variables as well as mutable
        # output variables as all views of one another
        # Note that we retrieve the input IDs before executing,
        # and refer to the output IDs as variables after executing
        # This will mean any accessed mutable variables will resolve
        # to the node they pointed to before the function call
        # and mutated ones will refer to the new GlobalNodes that
        # were created when processing `AccessedGlobals`
        mutable_output_vars: List[ExecutorPointer] = [
            Variable(k)
            for k, v in globals_result.added_or_modified.items()
            if is_mutable(v)
        ]
        side_effects.append(
            ViewOfNodes(mutable_input_vars + mutable_output_vars)
        )

        # Now append all side effects from the function
        for e in inspect_function(fn, args, kwargs, res):
            side_effects.append(self._translate_side_effect(node, e))

        return PrivateExecuteResult(res, start_time, end_time, side_effects)

    @_execute.register
    def _execute_import(
        self,
        node: ImportNode,
        changes: Iterable[TracebackChange],
        variables: Optional[Dict[str, LineaID]],
    ) -> PrivateExecuteResult:
        try:
            start_time = datetime.now()
            value = importlib.import_module(node.library.name)
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
            # Copy the result and the timing from the call node
            self._node_to_globals[node.call_id][node.name],
            *self._execution_time[node.call_id],
            [ViewOfNodes([ID(node.id), ID(node.call_id)])],
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
            return ID(node.positional_args[pointer.index])
        elif isinstance(pointer, KeywordArgument):
            return ID(node.keyword_args[pointer.name])
        elif isinstance(pointer, Result):
            return ID(node.id)
        elif isinstance(pointer, BoundSelfOfFunction):
            return ID(self._node_to_bound_self[node.function_id])
        elif isinstance(pointer, ExternalState):
            # If we have already created this external state, just return that ID
            if pointer in self._value_to_node:
                return ID(self._value_to_node[pointer])
            # Otherwise return a pointer that external state for the tracer
            # to create
            return pointer

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

    def lookup_value(self, name: str) -> object:
        """
        Lookup a value from a string identifier.
        """
        if hasattr(builtins, name):
            return getattr(builtins, name)
        if hasattr(operator, name):
            return getattr(operator, name)
        if name in LINEA_BUILTINS:
            return LINEA_BUILTINS[name]
        return self._globals[name]


@dataclass(frozen=True)
class MutatedNode:
    """
    Represents that a node has been mutated.
    """

    # The node that was mutated, the source node
    pointer: ExecutorPointer


@dataclass
class ViewOfNodes:
    """
    Represents that a set of nodes are now "views" of each other, meaning that
    if any are mutated they all could be mutated.
    """

    # An ordered set
    pointers: List[ExecutorPointer]


@dataclass
class ImplicitDependencyNode:
    """
    Represents that the call node has an implicit dependency on another node.
    """

    pointer: ExecutorPointer


@dataclass
class AccessedGlobals:
    """
    Represents some global variables that were retireved or changed during this call.
    """

    retrieved: List[str]
    added_or_updated: List[str]


SideEffect = Union[
    MutatedNode, ViewOfNodes, AccessedGlobals, ImplicitDependencyNode
]
SideEffects = List[SideEffect]


@dataclass
class ID:
    id: LineaID


@dataclass
class Variable:
    name: str


# Instead of just passing back the linea ID for the side effect, we create
# a couple of different cases, to cover different things we might want to point
# to.
ExecutorPointer = Union[ID, Variable, ExternalState]
