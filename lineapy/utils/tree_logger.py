"""
Logging util for outputing function calls as trees!
"""

from functools import wraps
from typing import Callable, TypeVar, cast

from rich.tree import Tree

TOP_TREE = Tree("All Calls")
CURRENT_TREE = TOP_TREE

C = TypeVar("C", bound=Callable)


def tree_log(fn: C, style=None) -> C:
    @wraps(fn)
    def inner(*args, **kwargs):
        global CURRENT_TREE

        prev_tree = CURRENT_TREE
        CURRENT_TREE = CURRENT_TREE.add(
            render_call(fn, args, kwargs), style=style
        )
        res = fn(*args, **kwargs)
        if res is not None:
            CURRENT_TREE.add(f"{res}", style="bold")
        CURRENT_TREE = prev_tree
        return res

    return cast(C, inner)


CLASS_TO_COLOR = {
    "NodeTransformer": "blue",
    "NodeVisitor": "blue",
    "Tracer": "green",
    "Executor": "yellow",
}


def render_call(fn, args, kwargs):
    cls_str, fn_str = fn.__qualname__.split(".")
    colored_fn = f"[{CLASS_TO_COLOR[cls_str]}]{cls_str}.[bold underline]{fn_str}[/bold underline][/]"

    args_str = ", ".join(
        [repr(a) for a in args] + [f"{k}={v}" for k, v in kwargs.items()]
    )
    return f"{colored_fn}({args_str})"


class TreeLog:
    def __getattribute__(self, item):
        value = object.__getattribute__(self, item)
        if callable(value):
            return tree_log(value)
        return value
