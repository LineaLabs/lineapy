import operator
from collections import Counter
from typing import List

import numpy
import pytest

from lineapy.system_tracing.exec_and_record_function_calls import (
    exec_and_record_function_calls,
)
from lineapy.system_tracing.function_call import FunctionCall
from tests.util import EqualsArray, IsInstance

is_list_iter = IsInstance(type(iter([])))


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
            [
                FunctionCall(iter, [[1, 2]], {}, is_list_iter),
                FunctionCall(next, [is_list_iter], {}, 1),
                FunctionCall(next, [is_list_iter], {}, 2),
            ],
            id="GET_ITER and FOR_ITER",
        ),
        pytest.param(
            "x**y",
            {"x": 3, "y": 2},
            [FunctionCall(operator.pow, [3, 2], {}, 9)],
            id="BINARY_POWER",
        ),
        pytest.param(
            "x * y",
            {"x": 2, "y": 4},
            [FunctionCall(operator.mul, [2, 4], {}, 8)],
            id="BINARY_MULTIPLY",
        ),
        pytest.param(
            "x @ y",
            {"x": numpy.array([1, 2]), "y": numpy.array([3, 4])},
            [
                FunctionCall(
                    operator.matmul,
                    [
                        EqualsArray(numpy.array([1, 2])),
                        EqualsArray(numpy.array([3, 4])),
                    ],
                    {},
                    EqualsArray(11),
                )
            ],
            id="BINARY_MATRIX_MULTIPLY",
        ),
        pytest.param(
            "x // y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.floordiv, [5, 2], {}, 2)],
            id="BINARY_FLOOR_DIVIDE",
        ),
        pytest.param(
            "x / y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.truediv, [5, 2], {}, 2.5)],
            id="BINARY_TRUE_DIVIDE",
        ),
        pytest.param(
            "x % y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.mod, [5, 2], {}, 1)],
            id="BINARY_MODULO",
        ),
        pytest.param(
            "x + y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.add, [5, 2], {}, 7)],
            id="BINARY_ADD",
        ),
        pytest.param(
            "x - y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.sub, [5, 2], {}, 3)],
            id="BINARY_SUBTRACT",
        ),
        pytest.param(
            "x[y]",
            {"x": [1], "y": 0},
            [FunctionCall(operator.getitem, [[1], 0], {}, 1)],
            id="BINARY_SUBSCR",
        ),
        pytest.param(
            "x << y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.lshift, [5, 2], {}, 20)],
            id="BINARY_LSHIFT",
        ),
        pytest.param(
            "x >> y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.rshift, [5, 2], {}, 1)],
            id="BINARY_RSHIFT",
        ),
        pytest.param(
            "x & y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.and_, [5, 2], {}, 0)],
            id="BINARY_RSHIFT",
        ),
        pytest.param(
            "x ^ y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.xor, [5, 2], {}, 7)],
            id="BINARY_RSHIFT",
        ),
        pytest.param(
            "x | y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.or_, [5, 2], {}, 7)],
            id="BINARY_RSHIFT",
        ),
    ],
)
def test_exec_and_record_function_calls(
    source_code: str, globals_, function_calls: List[FunctionCall]
):
    code = compile(source_code, "", "exec")
    trace_fn = exec_and_record_function_calls(code, globals_)
    assert not trace_fn.not_implemented_ops
    assert function_calls == trace_fn.function_calls
