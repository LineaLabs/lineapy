from __future__ import annotations

import builtins
import importlib.util
import io
import logging
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from datetime import datetime
from os import chdir, getcwd
from typing import Callable, Union, cast

import lineapy.lineabuiltins as lineabuiltins
from lineapy.data.graph import Graph
from lineapy.data.types import (
    CallNode,
    Execution,
    ImportNode,
    LineaID,
    LiteralNode,
    LookupNode,
    Node,
    NodeValue,
)
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.instrumentation.inspect_function import (
    KeywordArg,
    PositionalArg,
    ResultType,
    inspect_function,
)
from lineapy.utils import get_new_id, get_value_type

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

    def get_value(self, node: Node) -> object:
        return self._id_to_value[node.id]

    def execute_node(self, node: Node) -> SideEffects:
        """
        Executes a node, records its value and execution time.

        Only writes values for call nodes currently.
        """
        logger.info("Executing node %s", node)
        if isinstance(node, LookupNode):
            value = lookup_value(node.name)
            self._id_to_value[node.id] = value

            return SideEffects()
        elif isinstance(node, CallNode):
            fn = cast(Callable, self._id_to_value[node.function_id])

            args = [
                self._id_to_value[arg_id] for arg_id in node.positional_args
            ]
            kwargs = {
                k: self._id_to_value[arg_id]
                for k, arg_id in node.keyword_args.items()
            }
            logger.info("Calling function %s %s %s", fn, args, kwargs)

            with redirect_stdout(self._stdout):
                start_time = datetime.now()
                res = fn(*args, **kwargs)
                end_time = datetime.now()
            self.db.write_node_value(
                NodeValue(
                    node_id=node.id,
                    value=res,
                    execution_id=self.execution.id,
                    start_time=start_time,
                    end_time=end_time,
                    value_type=get_value_type(res),
                )
            )
            self._id_to_value[node.id] = res
            inspect_function_res = inspect_function(fn, args, kwargs, res)

            def from_inspect_pointer(
                pointer: Union[PositionalArg, KeywordArg, ResultType],
                node=node,
            ) -> LineaID:
                if isinstance(pointer, PositionalArg):
                    return node.positional_args[pointer.index].id
                elif isinstance(pointer, KeywordArg):
                    return node.keyword_args[pointer.name].id
                elif isinstance(pointer, ResultType):
                    return node.id

            return SideEffects(
                mutated={
                    from_inspect_pointer(m)
                    for m in inspect_function_res.mutated
                },
                views={
                    (
                        from_inspect_pointer(v.source),
                        from_inspect_pointer(v.viewer),
                    )
                    for v in inspect_function_res.views
                },
            )

        elif isinstance(node, ImportNode):
            with redirect_stdout(self._stdout):
                value = importlib.import_module(node.library.name)
            self._id_to_value[node.id] = value
            return SideEffects()
        elif isinstance(node, LiteralNode):
            self._id_to_value[node.id] = node.value
            return SideEffects()

    def execute_graph(self, graph: Graph) -> None:
        logger.info("Executing graph %s", graph)
        prev_working_dir = getcwd()
        chdir(graph.session_context.working_directory)
        for node in graph.visit_order():
            self.execute_node(node)
        chdir(prev_working_dir)
        # Add executed nodes to DB
        self.db.session.commit()


@dataclass(frozen=True)
class SideEffects:
    """
    The side effects from executing a node,
    """

    # Set of linea IDs which were mutated by executing this node.
    mutated: set[LineaID] = field(default_factory=set)
    # Set of mappings from the ID of a source node to the ID of a new node
    # which is now a view of that node
    # This means that now whenever the source is mutated, the viewer is also mutated.
    views: set[tuple[LineaID, LineaID]] = field(default_factory=set)


def lookup_value(name: str) -> object:
    """
    Lookup a value from a string identifier.
    """
    if hasattr(builtins, name):
        return getattr(builtins, name)
    if hasattr(lineabuiltins, name):
        return getattr(lineabuiltins, name)
    return globals()[name]
