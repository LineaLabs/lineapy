import operator
from collections import Counter
from dataclasses import dataclass
from typing import Iterator, List

import pytest

from lineapy.system_tracing.exec_and_record_function_calls import (
    exec_and_record_function_calls,
)
from lineapy.system_tracing.function_call import FunctionCall


@dataclass
class IsType:
    """
    Used in the tests so we can make sure a value has the same type as another, even if it is not equal.
    """

    tp: type

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.tp)


@pytest.mark.parametrize(
    "source_code,globals_,function_calls",
    [
        pytest.param(
            # Example where unary positive returns different result than arg https://stackoverflow.com/a/18818979
            "+c",
            {"c": Counter({"a": -1})},
            [FunctionCall(operator.pos, [Counter({"a": -1})], {}, Counter())],
            id="UNARY_POSITIVE",
        ),
        pytest.param(
            "-x",
            {"x": -1},
            [FunctionCall(operator.neg, [-1], {}, 1)],
            id="UNARY_NEGATIVE",
        ),
        pytest.param(
            "not x",
            {"x": True},
            [FunctionCall(operator.not_, [True], {}, False)],
            id="UNARY_NOT",
        ),
        pytest.param(
            "~x",
            {"x": 1},
            [FunctionCall(operator.inv, [1], {}, -2)],
            id="UNARY_INVERT",
        ),
        pytest.param(
            "for _ in x: pass",
            {"x": [1, 2]},
            [FunctionCall(iter, [[1, 2]], {}, IsType(type(iter([]))))],
            id="GET_ITER",
        ),
    ],
)
def test_exec_and_record_function_calls(
    source_code: str, globals_, function_calls: List[FunctionCall]
):
    code = compile(source_code, "", "exec")
    assert exec_and_record_function_calls(code, globals_) == function_calls
