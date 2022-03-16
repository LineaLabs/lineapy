from types import CodeType
from typing import List, Mapping

from lineapy.system_tracing.function_call import FunctionCall
from lineapy.system_tracing.record_function_calls import record_function_calls


def exec_and_record_function_calls(
    code: CodeType, globals_: Mapping[str, object] = None
) -> List[FunctionCall]:
    """
    Execute the code while recording all the function calls which originate from the code object.
    """
    with record_function_calls(code=code) as function_calls:
        exec(code, globals_ if globals_ is not None else {})
    return function_calls
