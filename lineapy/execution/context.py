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

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Mapping, Optional

from lineapy.execution.globals_dict import GlobalsDict

if TYPE_CHECKING:
    from lineapy.data.types import CallNode, LineaID
    from lineapy.execution.executor import Executor

_global_variables: GlobalsDict = GlobalsDict()
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
    _input_node_ids: Mapping[str, LineaID]

    @property
    def global_variables(self) -> Dict[str, object]:
        """
        The current globals dictionary
        """
        return _global_variables


def set_context(
    executor: Executor,
    variables: Optional[Dict[str, LineaID]],
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
    # The first time this is run, variables is set, and we know
    # the scoping, so we set all of the variables we know.
    # The subsequent times, we only use those that were recorded
    input_node_ids = variables or node.global_reads
    input_globals = {
        k: executor._id_to_value[id_] for k, id_ in input_node_ids.items()
    }

    _global_variables.setup_globals(input_globals)

    _current_context = ExecutionContext(
        node=node,
        executor=executor,
        _input_globals=input_globals,
        _input_node_ids=input_node_ids,
    )


def get_context() -> ExecutionContext:
    if not _current_context:
        raise RuntimeError("No context set")

    return _current_context


def teardown_context() -> ContextResult:
    """
    Tearsdown the context, returning the nodes that were accessed
    and a mapping variables to new values that were added or crated
    """
    global _current_context
    if not _current_context:
        raise RuntimeError("No context set")
    # Place in try/finally block so that context is always removed,
    # in case one test fails here, but the next should succeed
    try:
        res = _global_variables.teardown_globals()
        # To get the accessed inputs, we map each k that was accessed to its node ID
        accessed_inputs = {
            k: _current_context._input_node_ids[k] for k in res.accessed_inputs
        }
    finally:
        _current_context = None
    return ContextResult(accessed_inputs, res.added_or_modified)


@dataclass
class ContextResult:
    accessed_inputs: Dict[str, LineaID]
    added_or_modified: Dict[str, object]
