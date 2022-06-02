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
def test_walrus(execute):
    code1 = """
import lineapy
x = (y := 10)
(z := x) < 10
(x := 7) > 9
(a := z)
(z := x) > 9
lineapy.save(z, 'z')
"""

    res1 = execute(code1, snapshot=False)
    assert res1.values["z"] == 7
    assert res1.artifacts["z"] == """(x := 7) > 9\n(z := x) > 9\n"""

    code2 = """
z = 10
z = (x := 8)
"""
    res2 = execute(code2, snapshot=False)
    assert res2.values["z"] == 8
