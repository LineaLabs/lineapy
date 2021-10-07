import builtins
import importlib.util
import io
import logging
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from datetime import datetime
from os import chdir, getcwd
from typing import Callable, cast

import lineapy.lineabuiltins as lineabuiltins
from lineapy.data.graph import Graph
from lineapy.data.types import (
    CallNode,
    ImportNode,
    LineaID,
    LookupNode,
    Node,
    NodeType,
    SessionContext,
)

logger = logging.getLogger(__name__)


@dataclass
class Executor:
    """
    An executor that is responsible for executing a graph, either node by
    node as it is created, or in a batch, after the fact.
    """

    _id_to_value: dict[LineaID, object] = field(default_factory=dict)
    _stdout: io.StringIO = field(default_factory=io.StringIO)

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

    def execute_node(self, node: Node) -> None:
        """
        Executes a node, records its value and execution time.
        """
        logger.info("Executing node %s", node)
        if isinstance(node, LookupNode):
            node.value = lookup_value(node.name)
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
                node.start_time = datetime.now()
                node.value = fn(*args, **kwargs)
                node.end_time = datetime.now()

        elif node.node_type == NodeType.ImportNode:
            node = cast(ImportNode, node)
            with redirect_stdout(self._stdout):
                node.start_time = datetime.now()
                node.value = importlib.import_module(node.library.name)
                node.end_time = datetime.now()
        self._id_to_value[node.id] = node.value

    def execute_graph(self, graph: Graph) -> None:
        logger.info("Executing graph %s", graph)
        prev_working_dir = getcwd()
        chdir(graph.session_context.working_directory)

        for node in graph.visit_order():
            # # If we have already executed this node, dont do it again
            # # This shows up during jupyter cell exection
            # if node.value is not None:
            #     continue
            self.execute_node(node)
        chdir(prev_working_dir)


def lookup_value(name: str) -> object:
    """
    Lookup a value from a string identifier.
    """
    if hasattr(builtins, name):
        return getattr(builtins, name)
    if hasattr(lineabuiltins, name):
        return getattr(lineabuiltins, name)
    return globals()[name]
