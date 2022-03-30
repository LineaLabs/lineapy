import logging
from sys import settrace
from types import CodeType
from typing import Dict

from lineapy.system_tracing._trace_func import TraceFunc

logger = logging.getLogger(__name__)


def exec_and_record_function_calls(
    code: CodeType, globals_: Dict[str, object]
) -> TraceFunc:
    """
    Execute the code while recording all the function calls which originate from the code object.
    """
    logger.debug("Execing code")
    trace_func = TraceFunc(code)
    try:
        settrace(trace_func)
        exec(code, globals_)
    # Always stop tracing even if exception raised
    finally:
        settrace(None)
    return trace_func
