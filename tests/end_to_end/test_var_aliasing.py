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
