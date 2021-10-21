import pytest


def test_function_definition_without_side_effect_artifacts(execute):
    code = """b=30
def foo(a):
    return a - 10
c = foo(b)
"""
    res = execute(code, artifacts=["c"])
    assert res.values["c"] == 20
    assert res.artifacts["c"] == code


@pytest.mark.xfail
def test_function_definition_with_globals(execute):
    code = """b=10
def foo(a):
    return a - b
c = foo(15)
"""
    res = execute(code, artifacts=["c"])
    assert res.values["c"] == 5
    assert res.artifacts["c"] == code
