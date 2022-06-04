def test_alias_by_reference(execute):
    ALIAS_BY_REFERENCE = """a = [1,2,3]
b = a
a.append(4)
c = 2
r1 = c in a
r2 = c not in a
s = sum(b)
"""
    res = execute(ALIAS_BY_REFERENCE)
    assert res.values["s"] == 10
    assert res.values["r1"] is True
    assert res.values["r2"] is False


def test_alias_by_value(execute):
    ALIAS_BY_VALUE = """a = 0
b = a
a = 2
"""
    res = execute(ALIAS_BY_VALUE)
    assert res.values["a"] == 2
    assert res.values["b"] == 0


def test_variable_alias(execute):
    VARIABLE_ALIAS_CODE = """a = 1.2
b = a
"""
    res = execute(VARIABLE_ALIAS_CODE)
    assert res.values["a"] == 1.2
    assert res.values["b"] == 1.2


def test_var_alias_code(execute):
    code = """import lineapy
x = 100
y = x
x = 200
lineapy.save(y, "y")
"""
    res = execute(code)
    assert res.slice("y") == "x = 100\ny = x\n"
    assert res.values["x"] == 200
    assert res.values["y"] == 100


def test_alias_modifications_reflected_in_original_variable(execute):
    code = """
a = []
a.append(5)
b = a
a.append(10)
"""
    res = execute(code, artifacts=["a", "b"])
    assert res.values["a"] == res.values["b"] == [5, 10]
    assert res.slice("a") == "a = []\na.append(5)\na.append(10)\n"
    assert res.slice("b") == "a = []\na.append(5)\nb = a\na.append(10)\n"
