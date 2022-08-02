import pytest


def test_sub(execute):
    res = execute("x = 1\ny=-x")
    assert res.values["y"] == -1


def test_add(execute):
    """
    Weird test case from https://stackoverflow.com/a/16819334/907060
    """
    execute(
        """from decimal import Decimal
obj = Decimal('3.1415926535897932384626433832795028841971')
assert +obj != obj"""
    )


def test_invert(execute):
    """
    https://stackoverflow.com/q/7278779/907060
    """
    res = execute("a = 1\nb=~a")
    assert res.values["b"] == -2


def test_not(execute):
    res = execute("a = 1\nb=not a")
    assert res.values["b"] is False


def test_boolop_execute(execute):
    code = """print(True and False)
print(True or False)
x = True and False
"""
    res = execute(code)
    assert res.values["x"] is False


def test_boolop2_execute(execute):
    code = """x = 1>2
y = 1<2
z = x and y
q = (1>2 or 1<2)
"""
    res = execute(code)
    assert res.values["q"] is True
    assert res.values["z"] is False


def test_logical_binops(execute):
    code = """a = 1
b = 2
r1 = a == b
r2 = a != b
r3 = a < b
r4 = a <= b
r5 = a > b
r6 = a >= b
"""
    res = execute(code)
    assert res.values["r1"] is False
    assert res.values["r2"] is True
    assert res.values["r3"] is True
    assert res.values["r4"] is True
    assert res.values["r5"] is False
    assert res.values["r6"] is False


def test_binops(execute):

    code = """a = 11
b = 2

r1 = a + b
r2 = a - b
r3 =a * b
r4 =a / b
r5 =a // b
r6 =a % b
r7 =a ** b
r8 =a << b
r9 =a >> b
r10 =a | b
r11 =a ^ b
r12 =a & b
"""
    res = execute(code)
    assert res.values["r1"] == 13
    assert res.values["r2"] == 9
    assert res.values["r3"] == 22
    assert res.values["r4"] == 5.5
    assert res.values["r5"] == 5
    assert res.values["r6"] == 1
    assert res.values["r7"] == 121
    assert res.values["r8"] == 44
    assert res.values["r9"] == 2
    assert res.values["r10"] == 11
    assert res.values["r11"] == 9
    assert res.values["r12"] == 2


@pytest.mark.skipif("sys.version_info < (3, 8)")
def test_walrus_assigning_to_internal_identifier(execute):
    code = """
x = (y := 10)
(z := x) < 10
(x := 7) > 9
(a := z)
(z := x) > 9
"""

    res = execute(code, snapshot=False, artifacts=["z"])
    assert res.values["z"] == 7
    assert res.artifacts["z"] == """(x := 7) > 9\n(z := x) > 9\n"""


@pytest.mark.skipif("sys.version_info < (3, 8)")
def test_walrus_assigning_using_returned_value(execute):
    code = """
z = 10
z = (x := 8)
"""
    res = execute(code, snapshot=False, artifacts=["x", "z"])
    assert res.values["z"] == 8
    assert res.artifacts["x"] == "z = (x := 8)\n"
    assert res.artifacts["z"] == "z = (x := 8)\n"


@pytest.mark.skipif("sys.version_info < (3, 8)")
def test_walrus_list_comprehensions(execute):
    code = "(x := [t for t in range(3)])"

    res = execute(code, snapshot=False)
    assert res.values["x"] == [0, 1, 2]


@pytest.mark.skipif("sys.version_info < (3, 8)")
def test_walrus_multiple_identifiers(execute):
    code = """
x = 1
(x,y:=(1,2))
"""
    res = execute(code, snapshot=False, artifacts=["y"])
    assert res.values["x"] == 1
    assert res.values["y"] == (1, 2)
    assert res.artifacts["y"] == "x = 1\n(x, y := (1, 2))\n"


@pytest.mark.skipif("sys.version_info < (3, 8)")
def test_walrus_if_condition(execute):
    code = """
import sys
import pandas
if ( lib := sys.modules['pandas']):
    print(lib.__version__)
"""
    res = execute(code, snapshot=False)
    assert res.values["lib"].__name__ == "pandas"


@pytest.mark.skipif("sys.version_info < (3, 8)")
def test_walrus_if_condition_list_comp(execute):
    code = """
import math
[res for x in range(10) if (res:= math.sin(x)) >= 0]
"""
    res = execute(code, snapshot=False)
    from math import sin

    assert res.values["res"] == sin(9)


def test_conditional_expression_true_branch(execute):
    code = """a = 10
b = 20
c = 30
res = b if a <= 10 else c"""
    res = execute(code)
    assert res.values["res"] == 20


def test_conditional_expression_false_branch(execute):
    code = """a = 10
b = 20
c = 30
res = b if a > 10 else c"""
    res = execute(code)
    assert res.values["res"] == 30
