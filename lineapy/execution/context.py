"""
This module contains a number of globals, which are set by the execution when its
processing nodes. 

They are used as a side channel to pass values from the executor to special functions
which need to know more about the exeuction context, like in the `exec` to know
the source code of the current node.

This module exposes three global functions, which are meant to be used like:

1. The `executor` calls `set_context` before executing every call node.
2. The function being called can call `get_context` to get the current context.
3. The `executor` calls `teardown_context` after its finished executing
"""
from __future__ import annotations

import builtins
from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping, Optional

from lineapy.execution.record_dict import RecordGetitemDict

if TYPE_CHECKING:
    from lineapy.data.types import CallNode, LineaID
    from lineapy.execution.executor import Executor

_global_variables: RecordGetitemDict = RecordGetitemDict()
_current_context: Optional[ExecutionContext] = None


@dataclass
class ExecutionContext:
    """
    The context available to call nodes during an execution
    """

    # The current node being executed
    node: CallNode
    # The executor that is running
    executor: Executor

    _input_globals: Mapping[str, object]

    @property
    def global_variables(self) -> dict[str, object]:
        """
        The current globals dictionary
        """
        return _global_variables


def set_context(
    executor: Executor,
    variables: Optional[dict[str, LineaID]],
    node: CallNode,
) -> None:
    """
    Sets the context of the executor to the given node.
    """
    global _current_context
    if _current_context:
        raise RuntimeError("Context already set")

    # Set up our global variables, by first clearing out the old, and then
    # by updating with our new inputs
    # Note: We need to save our inputs so that we can check what has changed
    # at the end
    assert not _global_variables
    input_globals = {
        k: executor._id_to_value[id_]
        for k, id_ in (
            # The first time this is run, variables is set, and we know
            # the scoping, so we set all of the variables we know.
            # The subsequent times, we only use those that were recorded
            variables
            or node.global_reads
        ).items()
    }

    # Set __builtins__ directly so functions still have
    input_globals["__builtins__"] = builtins
    _global_variables.update(input_globals)

    _current_context = ExecutionContext(
        node=node,
        executor=executor,
        _input_globals=input_globals,
    )


def get_context() -> ExecutionContext:
    if not _current_context:
        raise RuntimeError("No context set")

    return _current_context


def teardown_context() -> tuple[dict[str, object], list[str]]:
    """
    Tearsdown the context, and returns a dict of the globals which have been updated
    and a list of them which have been accessed
    """

    global _current_context
    if not _current_context:
        raise RuntimeError("No context set")

    # Calculate what globals have changed or have been added. Compare by pointer,
    # not by value, since we want to see if the global variable has been re-assigned
    # not if the value has been mutated
    changed_globals = {
        k: v
        for k, v, in _global_variables.items()
        if
        # The global was changed if it is new, i.e. was not in the our variables
        k not in _current_context._input_globals
        # Or if it is different
        or _current_context._input_globals[k] is not v
    }

    # Retrieve before clearing
    getitems = _global_variables._getitems

    _global_variables.clear()
    _current_context = None
    return changed_globals, getitems
