import operator
from typing import List

import pytest

from lineapy.system_tracing.exec_and_record_function_calls import (
    exec_and_record_function_calls,
)
from lineapy.system_tracing.function_call import FunctionCall


@pytest.mark.parametrize(
    "source_code,function_calls",
    [
        pytest.param(
            "+10",
            [FunctionCall(operator.pos, [10], {}, 10)],
            id="UNARY_POSITIVE",
            marks=pytest.mark.xfail(),
        )
    ],
)
def test_exec_and_record_function_calls(
    source_code: str, function_calls: List[FunctionCall]
):
    code = compile(source_code, "", "exec")
    assert exec_and_record_function_calls(code) == function_calls
