"""
Logging util for outputing function calls as trees!


This is currently exposed through the `--tree-log` pytest command, which will log each test case to stdout.

We log every method of the CLASSES, so to change what is logged, modify that list.
Also, we color the statements, based on the class, using the CLASS_TO_COLOR mapping.
"""

from functools import wraps
from typing import Callable, Dict, Iterable, Optional, TypeVar, cast

import rich
from rich.tree import Tree

from lineapy.execution.executor import Executor
from lineapy.execution.inspect_function import FunctionInspector
from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.node_transformer import NodeTransformer

__all__ = ["start_tree_log", "print_tree_log"]


# Mapping from class name to the color we should use for its methods
# https://rich.readthedocs.io/en/stable/appendix/colors.html#appendix-colors
CLASS_TO_COLOR = {
    "NodeTransformer": "blue",
    "NodeVisitor": "blue",
    "Tracer": "green",
    "Executor": "yellow",
    "FunctionInspector": "red",
}

# List of classes we want to log
CLASSES = [NodeTransformer, Executor, Tracer, FunctionInspector]

# Current top tree we are logging from
TOP_TREE: Optional[Tree] = None
# The current tree for the function we are in.
CURRENT_TREE: Optional[Tree] = None

C = TypeVar("C", bound=Callable)


def start_tree_log(label: str) -> None:
    """
    Starts logging, by overriding the classes, and also sets the top level label for the tree.
    """
    global TOP_TREE, CURRENT_TREE
    TOP_TREE = Tree(label=label)
    CURRENT_TREE = TOP_TREE
    override_classes()


def print_tree_log() -> None:
    """
    Print the tree log with rich.
    """
    global TOP_TREE
    rich.print(TOP_TREE)


def tree_log(fn: C) -> C:
    """
    Decorator to enable logging for a function. Should preserve its behavior,
    but logs whenever it is called.
    """

    @wraps(fn)
    def inner(*args, **kwargs):
        global CURRENT_TREE
        assert CURRENT_TREE
        prev_tree = CURRENT_TREE
        CURRENT_TREE = CURRENT_TREE.add(render_call(fn, args, kwargs))
        res = fn(*args, **kwargs)
        if res is not None:
            CURRENT_TREE.add(f"{res}", style="bold")
        CURRENT_TREE = prev_tree
        return res

    return cast(C, inner)


def render_call(
    fn: Callable, args: Iterable[object], kwargs: Dict[str, object]
) -> str:
    """
    Render the function, args, and kwargs as a string for printing with rich.

    It uses some styles to color the classes and bold/underline the function names:
    https://rich.readthedocs.io/en/stable/style.html
    """
    qualname = fn.__qualname__
    parts = qualname.split(".")
    # If it's a classname.function, try coloring the classname
    if len(parts) == 2:
        cls_str, fn_str = parts
        colored_fn = f"[{CLASS_TO_COLOR.get(cls_str, 'black')}]{cls_str}.[bold underline]{fn_str}[/bold underline][/]"
    else:
        colored_fn = f"[bold underline]{qualname}[/bold underline]"

    args_str = ", ".join(
        [repr(a) for a in args] + [f"{k}={v}" for k, v in kwargs.items()]
    )
    return f"{colored_fn}({args_str})"


def override_classes():
    """
    Override the __getattribute__ on the classes we want to track, so that whenever a method is retrieved from them,
    it will wrap it in a logger first.
    """
    for c in CLASSES:
        c.__getattribute__ = _tree_log_getattribute  # type: ignore


def _tree_log_getattribute(self, item):
    value = super(type(self), self).__getattribute__(item)  # type: ignore
    if callable(value):
        return tree_log(value)
    return value
