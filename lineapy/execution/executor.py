from __future__ import annotations

import builtins
import importlib.util
import io
import logging
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from datetime import datetime
from functools import update_wrapper
from os import chdir, getcwd
from types import FunctionType
from typing import Callable, Iterable, Optional, Tuple, Union, cast

import lineapy.lineabuiltins as lineabuiltins
from lineapy.data.graph import Graph
from lineapy.data.types import (
    CallNode,
    Execution,
    ImportNode,
    LineaID,
    LiteralNode,
    LookupNode,
    MutateNode,
    Node,
)
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.instrumentation.inspect_function import (
    BoundSelfOfFunction,
    KeywordArg,
    MutatedPointer,
    Pointer,
    PositionalArg,
    Result,
    inspect_function,
)
from lineapy.utils import get_new_id

logger = logging.getLogger(__name__)


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

    _id_to_value: dict[LineaID, object] = field(default_factory=dict)
    _stdout: io.StringIO = field(default_factory=io.StringIO)
    _execution_time: dict[LineaID, Tuple[datetime, datetime]] = field(
        default_factory=dict
    )
    # Mapping of bound method node ids to the ID of the instance they are bound to
    _node_to_bound_self: dict[LineaID, LineaID] = field(default_factory=dict)

    def __post_init__(self):
        self.execution = Execution(
            id=get_new_id(),
            timestamp=datetime.now(),
        )
        self.db.write_execution(self.execution)

    def get_stdout(self) -> str:
        """
        This returns the text that corresponds to the stdout results.
        For instance, `print("hi")` should yield a result of "hi\n" from this function.

        Note:
        - If we assume that everything is sliced, the user printing may not
        happen, but third party libs may still have outputs.
        - Also the user may manually annotate for the print line to be
        included and in general stdouts are useful
        """

        val = self._stdout.getvalue()
        return val

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
        self, node: Node, variables: Optional[dict[str, LineaID]]
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
        logger.info("Executing node %s", node)
        if isinstance(node, LookupNode):
            value = lookup_value(node.name)
            self._id_to_value[node.id] = value

            return ()
        elif isinstance(node, CallNode):
            recorded_calls: list[LineaID] = []

            # execute the function
            # ----------
            fn = cast(
                Callable, self._lookup_value(node.function_id, recorded_calls)
            )

            # If we are getting an attribute, save the value in case
            # we later call it as a bound method and need to track its mutations
            if fn == getattr:
                self._node_to_bound_self[node.id] = node.positional_args[0]

            args = [
                self._lookup_value(arg_id, recorded_calls)
                for arg_id in node.positional_args
            ]
            kwargs = {
                k: self._lookup_value(arg_id, recorded_calls)
                for k, arg_id in node.keyword_args.items()
            }
            logger.info("Calling function %s %s %s", fn, args, kwargs)

            # If this was a user defined function, and we know that some global
            # variables need to be set before calling it, set those first
            # by modifying the globals that is specific to this function

            # The first time this is run, variables is set, and we know
            # the scoping, so we set all of the variables we know.

            # The subsequent times, we only use those that were recorded
            node_variables = {
                k: self._id_to_value[id_]
                for k, id_ in (variables or node.global_reads).items()
            }
            lineabuiltins.set_exec_globals(node_variables)

            with redirect_stdout(self._stdout):
                start_time = datetime.now()
                res = fn(*args, **kwargs)
                end_time = datetime.now()

            lineabuiltins.clear_exec_globals()

            self._execution_time[node.id] = (start_time, end_time)

            if recorded_calls:
                yield UsedDefinedFunctionsCalled(recorded_calls)
            # dependency analysis
            # ----------
            self._id_to_value[node.id] = res
            side_effects = inspect_function(fn, args, kwargs, res)

            def get_node_id(
                pointer: Pointer,
                node: CallNode = cast(CallNode, node),
            ) -> LineaID:
                if isinstance(pointer, PositionalArg):
                    return node.positional_args[pointer.index]
                elif isinstance(pointer, KeywordArg):
                    return node.keyword_args[pointer.name]
                elif isinstance(pointer, Result):
                    return node.id
                elif isinstance(pointer, BoundSelfOfFunction):
                    return self._node_to_bound_self[node.function_id]

            for e in side_effects:
                if isinstance(e, MutatedPointer):
                    yield MutatedNode(get_node_id(e.pointer))
                else:
                    yield ViewOfNodes(*map(get_node_id, e.pointers))

        elif isinstance(node, ImportNode):
            with redirect_stdout(self._stdout):
                value = importlib.import_module(node.library.name)
            self._id_to_value[node.id] = value
            return []
        elif isinstance(node, LiteralNode):
            self._id_to_value[node.id] = node.value
            return []
        elif isinstance(node, MutateNode):
            # Copy the value from the source value node
            self._id_to_value[node.id] = self._id_to_value[node.source_id]

            # The mutate node is a view of its source
            yield ViewOfNodes(node.id, node.source_id)

    def _lookup_value(
        self, id: LineaID, recorded_calls: list[LineaID]
    ) -> object:
        """
        Looks up a value, and if it is a use defined function, wrap it so
        we know when it is called
        """
        value = self._id_to_value[id]
        # If this is a user defined function, then wrap it, so we know if it was
        # called as an arg
        if isinstance(value, FunctionType):
            value = FunctionWrapper(value, id, recorded_calls)
        return value

    def execute_graph(self, graph: Graph) -> None:
        logger.info("Executing graph %s", graph)
        prev_working_dir = getcwd()
        chdir(graph.session_context.working_directory)
        for node in graph.visit_order():
            self.execute_node(node, variables=None)
        chdir(prev_working_dir)
        # Add executed nodes to DB
        self.db.session.commit()


@dataclass(frozen=True)
class MutatedNode:
    """
    Represents that a node has been mutated.
    """

    id: LineaID


@dataclass
class ViewOfNodes:
    """
    Represents that a set of nodes are now "views" of each other, meaning that
    if any are mutated they all could be mutated.
    """

    # An ordered set
    ids: list[LineaID]

    def __init__(self, *ids: LineaID):
        self.ids = list(ids)


@dataclass
class UsedDefinedFunctionsCalled:
    """
    Represents that a number of user defined function were called
    """

    ids: list[LineaID]


SideEffects = Iterable[
    Union[MutatedNode, ViewOfNodes, UsedDefinedFunctionsCalled]
]


def lookup_value(name: str) -> object:
    """
    Lookup a value from a string identifier.
    """
    if hasattr(builtins, name):
        return getattr(builtins, name)
    if hasattr(lineabuiltins, name):
        return getattr(lineabuiltins, name)
    return globals()[name]


@dataclass
class FunctionWrapper:
    """
    Wraps a user defined function, so we can record when it was called
    """

    # The original function value
    fn: FunctionType
    # The ID of the function node
    id: LineaID
    # Our list of calls, which we should add this ID to when it is called,
    # unless it has already been added
    recorded_calls: list[LineaID]

    def __post_init__(self):
        # Update this callable to use the functions docstrings and such
        update_wrapper(self, self.fn)

    def __call__(self, *args, **kwds):
        if self.id not in self.recorded_calls:
            self.recorded_calls.append(self.id)
        return self.fn(*args, **kwds)
