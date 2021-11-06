from __future__ import annotations

import importlib.util
import logging
from dataclasses import dataclass, field
from datetime import datetime
from os import chdir, getcwd
from typing import Callable, Iterable, Optional, Tuple, Union, cast

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
from lineapy.exceptions.user_exception import (
    AddFrame,
    RemoveFrames,
    RemoveFramesWhile,
    UserException,
)
from lineapy.execution.context import set_context, teardown_context
from lineapy.instrumentation.inspect_function import (
    BoundSelfOfFunction,
    Global,
    ImplicitDependencyPointer,
    KeywordArg,
    MutatedPointer,
    Pointer,
    PositionalArg,
    Result,
    inspect_function,
)
from lineapy.ipython_cell_storage import get_location_path
from lineapy.utils import get_new_id, listify, lookup_value

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
    _execution_time: dict[LineaID, Tuple[datetime, datetime]] = field(
        default_factory=dict
    )
    # Mapping of bound method node ids to the ID of the instance they are bound to
    _node_to_bound_self: dict[LineaID, LineaID] = field(default_factory=dict)

    # Mapping of call node to the globals that were updated
    # TODO: rename to variable
    _node_to_globals: dict[LineaID, dict[str, object]] = field(
        default_factory=dict
    )

    # Mapping of our implicit globals to their ids, if we have created them yet.
    _implicit_global_to_node: dict[object, LineaID] = field(
        default_factory=dict
    )

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

    # TODO: Refactor this to split out each type of node to its own function
    # Have them all return value and time, instead of setting inside
    @listify
    def execute_node(
        self,
        node: Node,
        variables: Optional[dict[str, LineaID]],
        implicit_globals: Optional[dict[object, LineaID]] = None,
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

        # To use if we need to raise an exception and change the frame
        add_frame: list[AddFrame] = []
        if node.source_location:
            location = node.source_location.source_code.location
            add_frame.append(
                AddFrame(
                    str(get_location_path(location).absolute()),
                    node.source_location.lineno,
                )
            )
        if isinstance(node, LookupNode):
            # If we get a lookup error, change it to a name error to match python
            try:
                start_time = datetime.now()
                value = lookup_value(node.name)
                end_time = datetime.now()
            except KeyError:
                # Matches Python's message
                message = f"name '{node.name}' is not defined"

                raise UserException(NameError(message), *add_frame)
            self._id_to_value[node.id] = value
        elif isinstance(node, CallNode):

            # execute the function
            # ----------
            fn = cast(Callable, self._id_to_value[node.function_id])

            # If we are getting an attribute, save the value in case
            # we later call it as a bound method and need to track its mutations
            if fn is getattr:
                self._node_to_bound_self[node.id] = node.positional_args[0]

            args = [
                self._id_to_value[arg_id] for arg_id in node.positional_args
            ]
            kwargs = {
                k: self._id_to_value[arg_id]
                for k, arg_id in node.keyword_args.items()
            }
            logger.info("Calling function %s %s %s", fn, args, kwargs)

            # Set up our execution context, with our globals and node
            set_context(self, variables, node)

            try:
                start_time = datetime.now()
                res = fn(*args, **kwargs)
                end_time = datetime.now()
            except Exception as exc:
                raise UserException(exc, RemoveFrames(1), *add_frame)
            finally:
                # Check what has been changed and accessed in the globals
                # Do this in a finally, so its always torn down even after exceptions
                changed_globals, retrieved_globals = teardown_context()

            self._execution_time[node.id] = (start_time, end_time)

            self._node_to_globals[node.id] = changed_globals
            added_or_updated = list(changed_globals.keys())

            yield AccessedGlobals(retrieved_globals, added_or_updated)

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
                elif isinstance(pointer, Global):
                    return self._get_implicit_global_node(node, pointer.value)

            for e in side_effects:
                if isinstance(e, MutatedPointer):
                    yield MutatedNode(get_node_id(e.pointer))
                elif isinstance(e, ImplicitDependencyPointer):
                    yield ImplicitDependency(get_node_id(e.pointer))
                else:
                    yield ViewOfNodes(*map(get_node_id, e.pointers))

        elif isinstance(node, ImportNode):
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
                    *add_frame,
                )
            self._id_to_value[node.id] = value
            self._execution_time[node.id] = datetime.now(), datetime.now()
        elif isinstance(node, LiteralNode):
            self._id_to_value[node.id] = node.value
            self._execution_time[node.id] = datetime.now(), datetime.now()
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

    def _get_implicit_global_node(self, call_node, obj: object) -> LineaID:
        if obj in self._implicit_global_to_node:
            return self._implicit_global_to_node[obj]
        else:
            global_lookup = LookupNode(
                id=get_new_id(),
                session_id=call_node.session_id,
                name=obj.__class__.__name__,
                source_location=None,
            )
            self.db.write_node(global_lookup)
            self.execute_node(node=global_lookup, variables=None)

            global_implicit_call_node = CallNode(
                id=get_new_id(),
                session_id=call_node.session_id,
                function_id=global_lookup.id,
                positional_args=[],
                keyword_args={},
                source_location=None,
                global_reads={},
                implicit_dependencies=[],
            )

            self.db.write_node(global_implicit_call_node)
            self.execute_node(node=global_implicit_call_node, variables=None)

            self._implicit_global_to_node[obj] = global_implicit_call_node.id
            return self._implicit_global_to_node[obj]

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
class ImplicitDependency:
    """
    Represents that the call node has an implicit dependency on another node.
    """

    id: LineaID


@dataclass
class AccessedGlobals:
    """
    Represents some global variables that were retireved or changed during this call.
    """

    retrieved: list[str]
    added_or_updated: list[str]


SideEffects = Iterable[
    Union[MutatedNode, ViewOfNodes, AccessedGlobals, ImplicitDependency]
]
