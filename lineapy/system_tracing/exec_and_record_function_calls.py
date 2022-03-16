from types import CodeType
from typing import List, Mapping

from lineapy.system_tracing.function_call import FunctionCall
from lineapy.system_tracing.record_function_calls import record_function_calls


def exec_and_record_function_calls(
    code: CodeType, globals_: Mapping[str, object]
) -> List[FunctionCall]:
    """
    Execute the code while recording all the function calls which originate from the code object.
    """
    with record_function_calls(code=code) as function_calls:
        exec(code, globals_)
    return function_calls
