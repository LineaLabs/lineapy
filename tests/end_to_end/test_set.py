import pytest


def test_set_init(execute):
    code = """x={1,1,2}
"""
    res = execute(code, artifacts=["x"])
    assert res.slice("x") == code
    assert res.values["x"] == {1, 2}


@pytest.mark.xfail(reason="sets not fully supported")
def test_set_add_mutates(execute):
    code = """x = set()
x.add(10)
"""
    res = execute(code, artifacts=["x"])
    assert res.slice("x") == code


@pytest.mark.xfail(reason="sets not fully supported")
def test_set_getitem_view(execute):
    code = """y = set()
x = [y]
y.add(10)
"""
    res = execute(code, artifacts=["x"])
    assert res.slice("x") == code


@pytest.mark.xfail(reason="sets not fully supported")
def test_set_add_mutates_inner(execute):
    code = """x = set()
y = [x]
x.add(10)
y[0].add(11)
"""
    res = execute(code, artifacts=["x", "y"])
    assert res.slice("x") == code
    assert res.slice("y") == code


@pytest.mark.xfail(reason="sets not fully supported")
def test_update_set_mutates(execute):
    code = """x = set()
x.update({1,1,2})
"""
    res = execute(code, artifacts=["x"])
    assert res.slice("x") == code
