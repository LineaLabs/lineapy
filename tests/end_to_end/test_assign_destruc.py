import traceback
from typing import cast

import pytest

from lineapy.exceptions.user_exception import UserException


def test_type_error_exception(execute):
    with pytest.raises(UserException) as e:
        execute("a , b = 1")

    inner_exception = cast(TypeError, e.value.__cause__)
    assert (
        traceback.extract_tb(inner_exception.__traceback__)[0].line
        == "a , b = 1"
    )


def test_name_error_exception(execute):
    with pytest.raises(UserException) as e:
        execute("a = b = c")

    inner_exception = cast(NameError, e.value.__cause__)
    assert (
        traceback.extract_tb(inner_exception.__traceback__)[0].line
        == "a = b = c"
    )


def test_syntax_error_exception(execute):
    with pytest.raises(UserException) as e:
        execute("a , *b = []]")

    inner_exception = cast(SyntaxError, e.value.__cause__)
    assert inner_exception.text == "a , *b = []]"


def test_type_error_exception_starred(execute):
    with pytest.raises(UserException) as e:
        execute("a,*b = 1")

    inner_exception = cast(TypeError, e.value.__cause__)
    assert (
        traceback.extract_tb(inner_exception.__traceback__)[0].line
        == "a,*b = 1"
    )


def test_value_error_exception_not_enough(execute):
    with pytest.raises(UserException) as e:
        execute("a , b = [1]")

    inner_exception = cast(ValueError, e.value.__cause__)
    assert (
        traceback.extract_tb(inner_exception.__traceback__)[0].line
        == "a , b = [1]"
    )


def test_value_error_exception_too_many(execute):
    with pytest.raises(UserException) as e:
        execute("a , b = [1,2,3]")

    inner_exception = cast(ValueError, e.value.__cause__)
    assert (
        traceback.extract_tb(inner_exception.__traceback__)[0].line
        == "a , b = [1,2,3]"
    )


def test_variable_alias_nested(execute):
    res = execute("a = 0\nb = a\nc = b")
    assert res.values["a"] == 0
    assert res.values["b"] == 0
    assert res.values["c"] == 0


def test_variable_alias_nested_list(execute):
    res = execute("a = [0,1]\nb = [a]\nc = [b]")
    assert res.values["a"] == [0, 1]
    assert res.values["b"] == [[0, 1]]
    assert res.values["c"] == [[[0, 1]]]


def test_assignment_destructuring_basic_tuple(execute):
    res = execute("a, b = (1, 2)")
    assert res.values["a"] == 1
    assert res.values["b"] == 2


def test_assignment_destructuring_basic(execute):
    res = execute("a, b , c = [1, 2, 3]")
    assert res.values["a"] == 1
    assert res.values["b"] == 2
    assert res.values["c"] == 3


def test_assignment_destructuring_with_reference(execute):
    res = execute("a = [1,2,5]\nb, c, d = a")
    assert res.values["a"] == [1, 2, 5]
    assert res.values["b"] == 1
    assert res.values["c"] == 2
    assert res.values["d"] == 5


def test_assignment_destructuring_with_alias(execute):
    res = execute("a=3\nb, c, d = [1, 2, a]")
    assert res.values["a"] == 3
    assert res.values["b"] == 1
    assert res.values["c"] == 2
    assert res.values["d"] == 3


def test_assignment_destructuring_starred_basic(execute):
    res = execute("a, *b, c = [1, 2, 3]")
    assert res.values["a"] == 1
    assert res.values["b"] == [2]
    assert res.values["c"] == 3


def test_assignment_destructuring_starred_list(execute):
    res = execute("a, *b, c = [1, 2, 3, 4]")
    assert res.values["a"] == 1
    assert res.values["b"] == [2, 3]
    assert res.values["c"] == 4


def test_assignment_destructuring_starred_basic_no_after(execute):
    res = execute("a, *b = [1, 2]")
    assert res.values["a"] == 1
    assert res.values["b"] == [2]


def test_assignment_destructuring_starred_list_no_after(execute):
    res = execute("a, *b = [1, 2, 3]")
    assert res.values["a"] == 1
    assert res.values["b"] == [2, 3]


def test_assignment_destructuring_starred_basic_no_before(execute):
    res = execute("*a, b = [1, 2]")
    assert res.values["a"] == [1]
    assert res.values["b"] == 2


def test_assignment_destructuring_starred_list_no_before(execute):
    res = execute("*a, b = [1, 2, 3]")
    assert res.values["a"] == [1, 2]
    assert res.values["b"] == 3


def test_assignment_destructuring_complex(execute):
    # [a, b], *rest = c
    res = execute("c = [[1, 2], 3]\n[a, b], *rest = c")
    assert res.values["a"] == 1
    assert res.values["b"] == 2
    assert res.values["rest"] == [3]


def test_assignment_destructuring_chained(execute):
    # a = b = c
    res = execute("x=1\nc = x\na = b = c")
    assert res.values["x"] == 1
    assert res.values["a"] == 1
    assert res.values["b"] == 1
    assert res.values["b"] == 1


def test_assignment_destructuring_chained_list(execute):
    # a = b = c
    res = execute("x=[1,2]\nc = x\na = b = c")
    assert res.values["x"] == [1, 2]
    assert res.values["a"] == [1, 2]
    assert res.values["b"] == [1, 2]
    assert res.values["b"] == [1, 2]


def test_assignment_destructuring_chained_complex_list(execute):
    # a,b = c, *d = e[:]
    res = execute("x=[1,2,3,4,5]\na , b = c, *d = x[:2]")
    assert res.values["x"] == [1, 2, 3, 4, 5]
    assert res.values["a"] == 1
    assert res.values["b"] == 2
    assert res.values["c"] == 1
    assert res.values["d"] == [2]


def test_assignment_destructuring_chained_complex_list_with_alias(execute):
    # a,b = c, *d = e[:]
    res = execute("x=[1,2,3,4,5]\ne = x\na , b = c, *d = e[:2]")
    assert res.values["x"] == [1, 2, 3, 4, 5]
    assert res.values["a"] == 1
    assert res.values["b"] == 2
    assert res.values["c"] == 1
    assert res.values["d"] == [2]
    assert res.values["e"] == [1, 2, 3, 4, 5]


def test_assignment_destructuring_slice(execute):
    code = """import lineapy
c = [1,2]
a, b = c
lineapy.save(a, "a")
lineapy.save(b, "b")
lineapy.save(c, "c")
"""
    res = execute(code)
    assert res.values["a"] == 1
    assert res.values["b"] == 2
    assert res.values["c"] == [1, 2]
    assert res.slice("a") == "c = [1,2]\na, b = c\n"
    assert res.slice("b") == "c = [1,2]\na, b = c\n"
    assert res.slice("c") == "c = [1,2]\n"


def test_assignment_destructuring_starred_slice(execute):
    code = """import lineapy
c = [1,2,3]
a, *b = c
lineapy.save(a, "a")
lineapy.save(b, "b")
lineapy.save(c, "c")
"""
    res = execute(code)
    assert res.values["a"] == 1
    assert res.values["b"] == [2, 3]
    assert res.values["c"] == [1, 2, 3]
    assert res.slice("a") == "c = [1,2,3]\na, *b = c\n"
    assert res.slice("b") == "c = [1,2,3]\na, *b = c\n"
    assert res.slice("c") == "c = [1,2,3]\n"
