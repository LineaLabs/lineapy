from __future__ import annotations

import builtins
import importlib.util
import io
import logging
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from datetime import datetime
from os import chdir, getcwd
from typing import Callable, Iterable, Optional, Tuple, Union, cast

import lineapy.lineabuiltins as lineabuiltins
from lineapy.data.graph import Graph
from lineapy.data.types import (
    CallNode,
    Execution,
    GlobalNode,
    ImportNode,
    LineaID,
    LiteralNode,
    LookupNode,
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
from lineapy.utils import get_new_id, lookup_value

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

    # Mapping of call node to the globals that were updated
    _node_to_globals: dict[LineaID, dict[str, object]] = field(
        default_factory=dict
    )

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
        elif isinstance(node, CallNode):

            # execute the function
            # ----------
            fn = cast(Callable, self._id_to_value[node.function_id])

            # If we are getting an attribute, save the value in case
            # we later call it as a bound method and need to track its mutations
            if fn == getattr:
                self._node_to_bound_self[node.id] = node.positional_args[0]

            args = [
                self._id_to_value[arg_id] for arg_id in node.positional_args
            ]
            kwargs = {
                k: self._id_to_value[arg_id]
                for k, arg_id in node.keyword_args.items()
            }
            logger.info("Calling function %s %s %s", fn, args, kwargs)

            ##
            # Setup our globals
            ##

            lineabuiltins._exec_globals.clear()
            lineabuiltins._exec_globals._getitems.clear()

            input_globals = {
                k: self._id_to_value[id_]
                for k, id_ in (
                    # The first time this is run, variables is set, and we know
                    # the scoping, so we set all of the variables we know.
                    # The subsequent times, we only use those that were recorded
                    variables
                    or node.global_reads
                ).items()
            }
            # Set __builtins__ directly so functions still have access to those
            input_globals["__builtins__"] = builtins

            lineabuiltins._exec_globals.update(input_globals)

            with redirect_stdout(self._stdout):
                start_time = datetime.now()
                res = fn(*args, **kwargs)
                end_time = datetime.now()
            self._execution_time[node.id] = (start_time, end_time)

            ##
            # Check what has been changed and accessed
            ##

            changed_globals = {
                k: v
                for k, v, in lineabuiltins._exec_globals.items()
                if
                # The global was changed if it is new, i.e. was not in the our variables
                k not in input_globals
                # Or if it is different
                or input_globals[k] is not v
            }
            self._node_to_globals[node.id] = changed_globals

            retrieved = lineabuiltins._exec_globals._getitems
            added_or_updated = list(changed_globals.keys())

            yield AccessedGlobals(retrieved, added_or_updated)

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
        elif isinstance(node, LiteralNode):
            self._id_to_value[node.id] = node.value
        elif isinstance(node, GlobalNode):
            self._id_to_value[node.id] = self._node_to_globals[node.call_id][
                node.name
            ]
            # The execution time is the time for the call node

            self._execution_time[node.id] = self._execution_time[node.call_id]

            yield ViewOfNodes(node.id, node.call_id)

        else:
            # Copy the value from the source value node
            self._id_to_value[node.id] = self._id_to_value[node.source_id]

            # The execution time is the time for the call node
            self._execution_time[node.id] = self._execution_time[node.call_id]

            # The mutate node is a view of its source
            yield ViewOfNodes(node.id, node.source_id)

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
class AccessedGlobals:
    """
    Represents some global variables that were retireved or changed during this call.
    """

    retrieved: list[str]
    added_or_updated: list[str]


SideEffects = Iterable[Union[MutatedNode, ViewOfNodes, AccessedGlobals]]
