"""
This module adds support for using sys.settrace to understand what happens 
during a subset of code execution that's passed in. In the context of how 
it's currently used, it's limited to the "blackbox" execs---`l_exec_statement`
It can be used used and tested independently.

At a high level, users could:

1. Use the `exec_and_record_function_calls.py` as an entry point and uses 
   `sys.settrace` to trace every bytecode execution and `_op_stack.py` to look at
   the bytecode stack during tracing. It translates different bytecode 
   instructions into the corresponding Python function calls.
2. Use `function_calls_to_side_effects.py` to translate the sequence of calls 
   that were recorded into the side effects produced on nodes (mapping Python
   changes to graph changes).
"""
