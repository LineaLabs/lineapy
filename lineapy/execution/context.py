"""
This module contains a number of globals, which are set by the execution when 
it is processing call nodes.

They are used as a side channel to pass values from the executor to special functions
which need to know more about the execution context, like in the `exec` to know
the source code of the current node.

This module exposes three global functions, which are meant to be used like:

1. The `executor` calls `set_context` before executing every call node.
2. The function being called can call `get_context` to get the current context.
3. The `executor` calls `teardown_context` after its finished executing

I.e. the context is created for every call.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import ModuleType
from typing import TYPE_CHECKING, Dict, Iterable, List, Mapping, Optional

from lineapy.execution.globals_dict import GlobalsDict, GlobalsDictResult
from lineapy.execution.inspect_function import is_mutable
from lineapy.execution.side_effects import (
    ID,
    AccessedGlobals,
    ExecutorPointer,
    MutatedNode,
    SideEffect,
    SideEffects,
    Variable,
    ViewOfNodes,
)
from lineapy.system_tracing.function_call import FunctionCall
from lineapy.system_tracing.function_calls_to_side_effects import (
    function_calls_to_side_effects,
)
from lineapy.utils.analytics import ExceptionEvent, track

if TYPE_CHECKING:
    from lineapy.data.types import CallNode, LineaID
    from lineapy.execution.executor import Executor
"""
Use the same globals for all executions, so that a function created during 
  one execution will have the same globals as when it is later called, 
  so we can see what globals have been written during that.
  Consider the following motivating example:
```python
a = 10
def f():
    print(a)
a = 15
f() # should print 15, instead of 10
```
"""

_global_variables: GlobalsDict = GlobalsDict()
_current_context: Optional[ExecutionContext] = None


@dataclass
class ExecutionContext:
    """
    This class is available during execution of CallNodes to the functions which are being called.

    It is used as a side channel to pass in metadata about the execution, such as the current node, and other global nodes
    (used during exec).

    The `side_effects` property is read after the function is finished, by the executor, so that the
    function can pass additional side effects that were triggered back to it indirectly. This is also
    used by the exec functions.
    """

    # The current node being executed
    node: CallNode
    # The executor that is running
    executor: Executor

    # Mapping from each input global name to its ID
    _input_node_ids: Mapping[str, LineaID]
    # Mapping from each input global name to whether it is mutable
    _input_globals_mutable: Mapping[str, bool]

    # Mapping of input node IDs to their values.
    # Used by the exec function to understand what side effects to emit, by knowing the nodes associated with each global value used.
    input_nodes: Mapping[LineaID, object]

    # Additional function calls made in this call, to be processed for side effects at the end.
    # The exec function will add to this and we will retrieve it at the end.
    function_calls: Optional[List[FunctionCall]] = field(default=None)

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

    global_name_to_value = {
        k: executor._id_to_value[id_] for k, id_ in input_node_ids.items()
    }
    _global_variables.setup_globals(global_name_to_value)

    global_node_id_to_value = {
        id_: executor._id_to_value[id_] for id_ in input_node_ids.values()
    }
    _current_context = ExecutionContext(
        _input_node_ids=input_node_ids,
        _input_globals_mutable={
            # Don't consider modules or classes as mutable inputs, so that any code which uses a module
            # we assume it doesn't mutate it.
            k: is_mutable(v) and not isinstance(v, (ModuleType, type))
            for k, v in global_name_to_value.items()
        },
        node=node,
        executor=executor,
        input_nodes=global_node_id_to_value,
    )


def get_context() -> ExecutionContext:
    if not _current_context:
        track(ExceptionEvent("DBError", "No context set"))
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
    res = _global_variables.teardown_globals()
    # If we didn't trace some function calls, use the legacy worst case assumptions for side effects
    if _current_context.function_calls is None:
        side_effects = list(_compute_side_effects(_current_context, res))
    else:
        # Compute the side effects based on the function calls that happened, to understand what input nodes
        # were mutated, what views were added, and what other side effects were created.
        side_effects = list(
            function_calls_to_side_effects(
                _current_context.executor._function_inspector,
                _current_context.function_calls,
                _current_context.input_nodes,
                res.added_or_modified,
            )
        )
    if res.accessed_inputs or res.added_or_modified:
        # Record that this execution accessed and saved certain globals, as first side effect
        side_effects.insert(
            0,
            AccessedGlobals(
                res.accessed_inputs,
                list(res.added_or_modified.keys()),
            ),
        )
    _current_context = None
    return ContextResult(res.added_or_modified, side_effects)


def _compute_side_effects(
    context: ExecutionContext, globals_result: GlobalsDictResult
) -> Iterable[SideEffect]:
    """
    This is the legacy worst case side effect computation and is applied when
    settrace's bytecode is not supported.

    Currently, anything related to generators is not supported, e.g.,
    ```python
    f(*x) # if we read the `next` function it will exhaust the generator and change
          # the semantics of the code.
    ```
    We can remove once we support tracking globals updated during calling
    user defined functions.
    """
    # Any nodes that we retrieved that were mutable, assume were mutated
    # Filter the vars by if the value is mutable
    mutable_input_vars: List[ExecutorPointer] = [
        ID(context._input_node_ids[name])
        for name in globals_result.accessed_inputs
        if context._input_globals_mutable[name]
    ]
    yield from map(MutatedNode, mutable_input_vars)

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
    if mutable_input_vars or mutable_output_vars:
        yield ViewOfNodes(mutable_input_vars + mutable_output_vars)


@dataclass
class ContextResult:
    # Mapping of global name to value for every global which was added or updated
    added_or_modified: Dict[str, object]
    # List of side effects added during the execution.
    side_effects: SideEffects
