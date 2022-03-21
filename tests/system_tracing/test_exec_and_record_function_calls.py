import operator
from collections import Counter
from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from types import FunctionType, TracebackType
from typing import Any, List, Set

import numpy
import pytest

from lineapy.system_tracing.exec_and_record_function_calls import (
    exec_and_record_function_calls,
)
from lineapy.system_tracing.function_call import FunctionCall
from lineapy.utils.lineabuiltins import l_dict, l_list, l_set
from tests.util import EqualsArray, IsInstance, IsMethod

is_list_iter = IsInstance(type(iter([])))
set_: Set[None] = set()
opened_file = open(NamedTemporaryFile().name, "w")


class IMatMul(EqualsArray):
    """
    Class to support inplace matrix multiply with Numpy matrices, for testing.
    """

    def __imatmul__(self, other: Any):
        self.array = self.array @ other
        return self


@dataclass
class DummyContextManager:
    """
    Context manager which will stop exception from being propogated and return the value
    """

    value: object

    def __enter__(self):
        return self.value

    def __exit__(self, *args):
        # Silence excpetion raised
        return True


context_manager = DummyContextManager(100)


@dataclass
class ContextManager:

    pass


@pytest.mark.parametrize(
    "source_code,globals_,function_calls",
    [
        ##
        # Unary Ops
        ##
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
        ##
        # Binary Ops
        ##
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
            id="BINARY_AND",
        ),
        pytest.param(
            "x ^ y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.xor, [5, 2], {}, 7)],
            id="BINARY_XOR",
        ),
        pytest.param(
            "x | y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.or_, [5, 2], {}, 7)],
            id="BINARY_OR",
        ),
        pytest.param(
            "x **= y",
            {"x": 3, "y": 2},
            [FunctionCall(operator.ipow, [3, 2], {}, 9)],
            id="INPLACE_POWER",
        ),
        pytest.param(
            "x *= y",
            {"x": 2, "y": 4},
            [FunctionCall(operator.imul, [2, 4], {}, 8)],
            id="INPLACE_MULTIPLY",
        ),
        pytest.param(
            "x @= y",
            {"x": IMatMul(numpy.array([1, 2])), "y": numpy.array([3, 4])},
            [
                FunctionCall(
                    operator.imatmul,
                    [
                        IMatMul(11),
                        EqualsArray(numpy.array([3, 4])),
                    ],
                    {},
                    IMatMul(11),
                )
            ],
            id="INPLACE_MATRIX_MULTIPLY",
        ),
        pytest.param(
            "x //= y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.ifloordiv, [5, 2], {}, 2)],
            id="INPLACE_FLOOR_DIVIDE",
        ),
        pytest.param(
            "x /= y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.itruediv, [5, 2], {}, 2.5)],
            id="INPLACE_TRUE_DIVIDE",
        ),
        pytest.param(
            "x %= y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.imod, [5, 2], {}, 1)],
            id="INPLACE_MODULO",
        ),
        pytest.param(
            "x += y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.iadd, [5, 2], {}, 7)],
            id="INPLACE_ADD",
        ),
        pytest.param(
            "x -= y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.isub, [5, 2], {}, 3)],
            id="INPLACE_SUBTRACT",
        ),
        pytest.param(
            "x <<= y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.ilshift, [5, 2], {}, 20)],
            id="INPLACE_LSHIFT",
        ),
        pytest.param(
            "x >>= y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.irshift, [5, 2], {}, 1)],
            id="INPLACE_RSHIFT",
        ),
        pytest.param(
            "x &= y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.iand, [5, 2], {}, 0)],
            id="INPLACE_AND",
        ),
        pytest.param(
            "x ^= y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.ixor, [5, 2], {}, 7)],
            id="INPLACE_XOR",
        ),
        pytest.param(
            "x |= y",
            {"x": 5, "y": 2},
            [FunctionCall(operator.ior, [5, 2], {}, 7)],
            id="INPLACE_OR",
        ),
        ##
        # Other inplace args
        ##
        pytest.param(
            "x[y] = z",
            {"x": {}, "y": 1, "z": 2},
            [FunctionCall(operator.setitem, [{1: 2}, 1, 2])],
            id="STORE_SUBSCR",
        ),
        pytest.param(
            "del x[y]",
            {"x": {1: 2}, "y": 1},
            [FunctionCall(operator.delitem, [{}, 1])],
            id="DELETE_SUBSCR",
        ),
        pytest.param(
            "{x for x in y}",
            {"y": [1]},
            [
                FunctionCall(iter, [[1]], {}, is_list_iter),
                FunctionCall(l_set, [], res={1}),
                FunctionCall(next, [is_list_iter], {}, 1),
                FunctionCall(getattr, [{1}, "add"], res=IsMethod({1}.add)),
                FunctionCall(IsMethod({1}.add), [1]),
                # This last call is to the function made internally by Python for the list iterator
                FunctionCall(
                    IsInstance(FunctionType), [is_list_iter], res={1}
                ),
            ],
            id="SET_ADD",
        ),
        pytest.param(
            "[x for x in y]",
            {"y": [1, 2]},
            [
                FunctionCall(iter, [[1, 2]], {}, is_list_iter),
                FunctionCall(l_list, [], res=[1, 2]),
                # First iteration
                FunctionCall(next, [is_list_iter], {}, 1),
                FunctionCall(
                    getattr, [[1, 2], "append"], res=IsMethod([1, 2].append)
                ),
                FunctionCall(IsMethod([1, 2].append), [1]),
                # Second iteration
                FunctionCall(next, [is_list_iter], {}, 2),
                FunctionCall(
                    getattr, [[1, 2], "append"], res=IsMethod([1, 2].append)
                ),
                FunctionCall(IsMethod([1, 2].append), [2]),
                # This last call is to the function made internally by Python for the list iterator
                FunctionCall(
                    IsInstance(FunctionType), [is_list_iter], res=[1, 2]
                ),
            ],
            id="LIST_APPEND",
        ),
        pytest.param(
            "{x: x + 1 for x in y}",
            {"y": [1]},
            [
                # Setup
                FunctionCall(iter, [[1]], {}, is_list_iter),
                FunctionCall(l_dict, [], res={1: 2}),
                # Iteration
                FunctionCall(next, [is_list_iter], {}, 1),
                FunctionCall(operator.add, [1, 1], res=2),
                FunctionCall(operator.setitem, [{1: 2}, 1, 2]),
                # Cleanup
                FunctionCall(
                    IsInstance(FunctionType), [is_list_iter], res={1: 2}
                ),
            ],
            id="MAP_ADD",
        ),
        pytest.param(
            "with x: pass",
            {"x": opened_file},
            [
                # Lookup exit method
                FunctionCall(
                    getattr,
                    [opened_file, "__exit__"],
                    {},
                    opened_file.__exit__,
                ),
                # Enter
                FunctionCall(
                    getattr,
                    [opened_file, "__enter__"],
                    {},
                    opened_file.__enter__,
                ),
                FunctionCall(opened_file.__enter__, [], {}, opened_file),
                # Exit
                FunctionCall(opened_file.__exit__, [None, None, None]),
            ],
            id="SETUP_WITH",
        ),
        pytest.param(
            "with x: raise NotImplementedError()",
            {"x": context_manager},
            [
                # Lookup exit method
                FunctionCall(
                    getattr,
                    [context_manager, "__exit__"],
                    {},
                    context_manager.__exit__,
                ),
                # Enter
                FunctionCall(
                    getattr,
                    [context_manager, "__enter__"],
                    {},
                    context_manager.__enter__,
                ),
                FunctionCall(
                    context_manager.__enter__, [], {}, context_manager.value
                ),
                # Exception
                FunctionCall(
                    NotImplementedError,
                    res=IsInstance(NotImplementedError),
                ),
                # Exit
                FunctionCall(
                    context_manager.__exit__,
                    [
                        NotImplementedError,
                        IsInstance(NotImplementedError),
                        IsInstance(TracebackType),
                    ],
                    {},
                    True,
                ),
            ],
            id="WITH_EXCEPT_START",
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
