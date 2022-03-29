import operator
from collections import Counter
from dataclasses import dataclass
from sys import version_info
from tempfile import NamedTemporaryFile
from types import FunctionType, SimpleNamespace, TracebackType
from typing import Any, List, Set

import numpy
import pytest

from lineapy.system_tracing.exec_and_record_function_calls import (
    exec_and_record_function_calls,
)
from lineapy.system_tracing.function_call import FunctionCall
from lineapy.utils.lineabuiltins import (
    l_dict,
    l_list,
    l_set,
    l_tuple,
    l_unpack_ex,
    l_unpack_sequence,
)
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


def create_list(a, b, c, d):
    """
    Function for testing kwargs
    """
    return [a, b, c, d]


def func_ex_test(a, b, c, d):
    return a + b + c + d


x_global = [1, 2]
x_global_generator = (i for i in x_global)
y_global = {
    "c": 3,
    "d": 4,
}


@dataclass
class DummyContextManager:
    """
    Context manager which will stop exception from being propagated and
    return the value
    """

    value: object

    def __enter__(self):
        return self.value

    def __exit__(self, *args):
        # Silence excpetion raised
        return True


context_manager = DummyContextManager(100)


method_property = SimpleNamespace(a=lambda: 10)


@dataclass
class ContextManager:

    pass


PYTHON_39 = version_info >= (3, 9)

# # Add this mark to bytecode ops which were removed in 3.9
# removed_in_39 = pytest.mark.skipif(version_info > (3, 8))
# # Add this mark to tests for bytecode ops that were added in 3.9
# added_in_39 = pytest.mark.skipif()


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
                FunctionCall(IsMethod([1, 2].append), [1]),
                # Second iteration
                FunctionCall(next, [is_list_iter], {}, 2),
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
                FunctionCall(opened_file.__enter__, [], {}, opened_file),
                FunctionCall(opened_file.__exit__, [None, None, None]),
            ],
            id="SETUP_WITH",
        ),
        pytest.param(
            "with x: raise NotImplementedError()",
            {"x": context_manager},
            [
                # Enter
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
        pytest.param(
            "x, y = z",
            {"z": (1, 2)},
            [
                FunctionCall(l_unpack_sequence, [(1, 2), 2], res=[1, 2]),
                FunctionCall(operator.getitem, [[1, 2], 0], res=1),
                FunctionCall(operator.getitem, [[1, 2], 1], res=2),
            ],
            id="UNPACK_SEQUENCE",
        ),
        pytest.param(
            "a, *b, c, d = e",
            {"e": range(6)},
            [
                FunctionCall(
                    l_unpack_ex, [range(6), 1, 2], res=[0, [1, 2, 3], 4, 5]
                ),
                FunctionCall(
                    operator.getitem, [[0, [1, 2, 3], 4, 5], 0], res=0
                ),
                FunctionCall(
                    operator.getitem, [[0, [1, 2, 3], 4, 5], 1], res=[1, 2, 3]
                ),
                FunctionCall(
                    operator.getitem, [[0, [1, 2, 3], 4, 5], 2], res=4
                ),
                FunctionCall(
                    operator.getitem, [[0, [1, 2, 3], 4, 5], 3], res=5
                ),
            ],
            id="UNPACK_EX",
        ),
        pytest.param(
            "x.y = z",
            {"x": SimpleNamespace(), "z": 10},
            [FunctionCall(setattr, [SimpleNamespace(y=10), "y", 10])],
            id="STORE_ATTR",
        ),
        pytest.param(
            "[x, y]",
            {"x": 1, "y": 2},
            [FunctionCall(l_list, [1, 2], res=[1, 2])],
            id="BUILD_LIST",
        ),
        pytest.param(
            "(x, y)",
            {"x": 1, "y": 2},
            [FunctionCall(l_tuple, [1, 2], res=(1, 2))],
            id="BUILD_TUPLE",
        ),
        pytest.param(
            "{x, y}",
            {"x": 1, "y": 2},
            [FunctionCall(l_set, [1, 2], res={1, 2})],
            id="BUILD_SET",
        ),
        pytest.param(
            "{a: b, c: d}",
            {"a": 1, "b": 2, "c": 1, "d": 4},
            [
                FunctionCall(l_tuple, [1, 2], res=(1, 2)),
                FunctionCall(l_tuple, [1, 4], res=(1, 4)),
                FunctionCall(l_dict, [(1, 2), (1, 4)], res={1: 4}),
            ],
            id="BUILD_MAP",
        ),
        pytest.param(
            "[y, *x]",
            {"x": [2], "y": 1},
            [
                FunctionCall(l_list, [1], res=[1, 2]),
                FunctionCall(IsMethod([1, 2].extend), [[2]]),
            ]
            if PYTHON_39
            else [
                FunctionCall(l_tuple, [1], res=(1,)),
                FunctionCall(list, res=[1, 2]),
                FunctionCall(IsMethod([1, 2].extend), [(1,)]),
                FunctionCall(IsMethod([1, 2].extend), [[2]]),
            ],
            id="LIST_EXTEND",
        ),
        pytest.param(
            "(*x, *y)",
            {"x": [1], "y": [2]},
            [
                FunctionCall(l_list, res=[1, 2]),
                FunctionCall(IsMethod([1, 2].extend), [[1]]),
                FunctionCall(IsMethod([1, 2].extend), [[2]]),
                FunctionCall(tuple, [[1, 2]], res=(1, 2)),
            ],
            id="BUILD_TUPLE_UNPACK",
        ),
        pytest.param(
            "{*x, *y}",
            {"x": [1], "y": [2]},
            [
                FunctionCall(l_set, [], res={1, 2}),
                FunctionCall(IsMethod({1, 2}.update), [[1]]),
                FunctionCall(IsMethod({1, 2}.update), [[2]]),
            ],
            id="SET_UPDATE",
        ),
        pytest.param(
            "{**x}",
            {"x": {1: 2}},
            [
                FunctionCall(l_dict, [], res={1: 2}),
                FunctionCall(IsMethod({1: 2}.update), [{1: 2}]),
            ],
            id="DICT_UPDATE",
        ),
        pytest.param(
            "x > y",
            {"x": 3, "y": 1},
            [
                FunctionCall(operator.gt, [3, 1], res=True),
            ],
            id="COMPARE_OP",
        ),
        pytest.param(
            "x is y",
            {"x": 3, "y": 1},
            [
                FunctionCall(operator.is_, [3, 1], res=False),
            ],
            id="IS_OP",
        ),
        pytest.param(
            "x in y",
            {"x": 3, "y": [1]},
            [
                FunctionCall(operator.contains, [[1], 3], res=False),
            ],
            id="CONTAINS_OP",
        ),
        pytest.param(
            "f(1, 2)",
            {"f": operator.add},
            [
                FunctionCall(operator.add, [1, 2], res=3),
            ],
            id="CALL_FUNCTION",
        ),
        pytest.param(
            "f(1, 2, c=3, d=4)",
            {"f": create_list},
            [
                FunctionCall(
                    create_list, [1, 2], {"c": 3, "d": 4}, res=[1, 2, 3, 4]
                ),
            ],
            id="CALL_FUNCTION_KW",
        ),
        pytest.param(
            "f(*x, **y)",
            {"f": func_ex_test, "x": x_global, "y": y_global},
            [
                FunctionCall(l_dict, args=[], kwargs={}, res={"c": 3, "d": 4}),
                FunctionCall(
                    fn=IsMethod(y_global.update),
                    args=[{"c": 3, "d": 4}],
                    kwargs={},
                    res=None,
                ),
                FunctionCall(func_ex_test, x_global, y_global, res=10),
            ],
            id="CALL_FUNCTION_EX",
        ),
        pytest.param(
            "f(*x, **y)",
            {"f": func_ex_test, "x": x_global_generator, "y": y_global},
            [],
            marks=pytest.mark.xfail(reason="should not analyze generators"),
            id="CALL_FUNCTION_EX_failure",
        ),
        pytest.param(
            "f(1,2, **y)",
            {"f": func_ex_test, "y": y_global},
            [
                FunctionCall(l_dict, args=[], kwargs={}, res={"c": 3, "d": 4}),
                FunctionCall(
                    fn=IsMethod(y_global.update),
                    args=[{"c": 3, "d": 4}],
                    kwargs={},
                    res=None,
                ),
                FunctionCall(func_ex_test, [1, 2], y_global, res=10),
            ],
            id="CALL_FUNCTION_EX_**",
        ),
        pytest.param(
            "f.a()",
            {"f": method_property},
            [FunctionCall(method_property.a, res=10)],
            id="CALL_METHOD function",
        ),
        pytest.param(
            "f.append(10)",
            {"f": []},
            [FunctionCall(IsMethod([10].append), [10])],
            id="CALL_METHOD method",
        ),
        pytest.param(
            "x[0:2]",
            {"x": [1, 2]},
            [
                FunctionCall(slice, [0, 2], res=slice(0, 2)),
                FunctionCall(
                    operator.getitem, [[1, 2], slice(0, 2)], res=[1, 2]
                ),
            ],
            id="BUILD_SLICE 2",
        ),
        pytest.param(
            "x[0:2:2]",
            {"x": [1, 2]},
            [
                FunctionCall(slice, [0, 2, 2], res=slice(0, 2, 2)),
                FunctionCall(
                    operator.getitem, [[1, 2], slice(0, 2, 2)], res=[1]
                ),
            ],
            id="BUILD_SLICE 3",
        ),
        pytest.param(
            "f'{x}'",
            {"x": "x"},
            [
                FunctionCall(format, ["x", None], res="x"),
            ],
            id="FORMAT_VALUE as-is no spec",
        ),
        pytest.param(
            "f'{x!r}'",
            {"x": "x"},
            [
                FunctionCall(repr, ["x"], res="'x'"),
                FunctionCall(format, ["'x'", None], res="'x'"),
            ],
            id="FORMAT_VALUE repr no spec",
        ),
        pytest.param(
            "f'{x!s}'",
            {"x": "x"},
            [
                FunctionCall(str, ["x"], res="x"),
                FunctionCall(format, ["x", None], res="x"),
            ],
            id="FORMAT_VALUE str no spec",
        ),
        pytest.param(
            "f'{x!a}'",
            {"x": "x"},
            [
                FunctionCall(ascii, ["x"], res="'x'"),
                FunctionCall(format, ["'x'", None], res="'x'"),
            ],
            id="FORMAT_VALUE ascii no spec",
        ),
        pytest.param(
            "f'{x!r:4}'",
            {"x": "x"},
            [
                FunctionCall(repr, ["x"], res="'x'"),
                FunctionCall(format, ["'x'", "4"], res="'x' "),
            ],
            id="FORMAT_VALUE repr spec",
        ),
    ],
)
def test_exec_and_record_function_calls(
    source_code: str, globals_, function_calls: List[FunctionCall]
):
    print(source_code)
    code = compile(source_code, "", "exec")
    trace_fn = exec_and_record_function_calls(code, globals_)
    assert not trace_fn.not_implemented_ops
    assert function_calls == trace_fn.function_calls
