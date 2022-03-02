import pytest

"""
Test the three parts of #95, to cover the Delete AST node

https://docs.python.org/3/library/ast.html#ast.Delete
"""


@pytest.mark.xfail(reason="dont support deleting a variable")
def test_del_var(execute):

    res = execute("a = 1; del a")
    assert "a" not in res.values


def test_del_subscript(execute):
    """
    Part of #95
    """
    res = execute("a = [1]; del a[0]")
    assert res.values["a"] == []


def test_set_attr(execute):
    res = execute("import types; x = types.SimpleNamespace(); x.hi = 1")
    assert res.values["x"].hi == 1


def test_del_attribute(execute):
    """
    Part of #95
    """
    res = execute(
        "import types; x = types.SimpleNamespace(); x.hi = 1; del x.hi",
    )
    x = res.values["x"]
    assert not hasattr(x, "hi")
