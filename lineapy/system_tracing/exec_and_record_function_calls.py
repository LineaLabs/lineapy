import logging
from sys import gettrace, settrace
from types import CodeType
from typing import Dict

from lineapy.system_tracing._trace_func import TraceFunc

logger = logging.getLogger(__name__)


def exec_and_record_function_calls(
    code: CodeType, globals_: Dict[str, object]
) -> TraceFunc:
    """
    Execute the code while recording all the function calls which originate from the code object.

    While recording function calls, we use sys.settrace() with LineaPy's tracer to extract relevant
    information during the runtime of the user's code's function, and reset the tracer after the user
    function has completed execution to prevent unnecessary logging.
    However, to ensure LineaPy works correctly while debugging using VSCode, we first capture any
    existing tracers using sys.gettrace(), perform our analysis using the LineaPy tracer, and reset
    the existing tracer using sys.settrace()
    """
    logger.debug("Executing code")
    original_trace = gettrace()
    trace_func = TraceFunc(code)
    try:
        settrace(trace_func)
        exec(code, globals_)
    # Always stop tracing even if exception raised
    finally:
        settrace(original_trace)
    return trace_func
