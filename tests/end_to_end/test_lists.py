def test_list_setitem_mutates(execute):
    code = """x = [1]
x[0] = 10
"""
    res = execute(code, artifacts=["x"])
    assert res.values["x"] == [10]
    assert res.slice("x") == code


def test_list_getitem_view(execute):
    code = """y = []
x = [y]
y.append(10)
"""
    res = execute(code, artifacts=["x"])
    assert res.slice("x") == code


def test_list_append_mutates(execute):
    code = """x = []
x.append(10)
"""
    res = execute(code, artifacts=["x"])
    assert res.slice("x") == code


def test_list_append_mutates_inner(execute):
    code = """x = []
y = [x]
x.append(10)
y[0].append(11)
"""
    res = execute(code, artifacts=["x", "y"])
    assert res.slice("x") == code
    assert res.slice("y") == code
