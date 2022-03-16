"""
This module adds support for using sys.settrace to understand what happens during some code execution. It was designed
to support the current use case of tracing during the `l_exec_statement` but also be compsable enough to be tested independently
and broken apart if need be.

At a high level, users should:

1. Use the `record_function_calls.py` context manager to record a number of function calls that during the `with` statement,
   limited recording to frames which are from the bytecode passed in. This uses `sys.settrace` to trace every bytecode execution and `_op_stack.py` to look at
   the bytecode stack during tracing. It translates different bytecode instructions into the corresponding Python
   function calls.
2. Use `function_calls_to_side_effects.py` to translate the sequence of calls that were recorded into the side effects
   produced on the nodes, by passing in the initial values that were nodes.
   In turn, this goes through a number of translation steps, first using `_function_calls_to_object_side_effects.py` to 
   to turn the function calls into the side effects in terms of the Python objects. For example, saying saying things like
   "The object [1, 2, 3] was mutated." Then, these are analyzed and turned into a list of side effects on nodes, like 
   "The node xyz-abc was mutated." using `_object_side_effects_to_side_effects.py`.

    # TODO: Add support for returning if any globals that are newly set are views.
"""
