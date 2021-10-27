def test_function_definition_without_side_effect_artifacts(execute):
    code = """b=30
def foo(a):
    return a - 10
c = foo(b)
"""
    res = execute(code, artifacts=["c"])
    assert res.values["c"] == 20
    assert res.artifacts["c"] == code


def test_function_definition_with_globals(execute):
    code = """b=10
def foo(a):
    return a - b
c = foo(15)
"""
    res = execute(code, artifacts=["c"])
    assert res.values["c"] == 5
    assert res.artifacts["c"] == code


def test_function_late_binding(execute):
    code = """def foo(a):
    return a - b
b=10
c = foo(15)
"""
    res = execute(code, artifacts=["c"])
    assert res.values["c"] == 5
    assert res.artifacts["c"] == code


def test_function_nested(execute):
    code = """def foo():
    def inner():
        return 1
    return inner
c = foo()()
"""
    res = execute(code, artifacts=["c"])
    assert res.values["c"] == 1
    assert res.artifacts["c"] == code


def test_function_nested_depend_global(execute):
    code = """def foo():
    def inner():
        return a
    return inner
a = 10
c = foo()()
"""
    res = execute(code, artifacts=["c"])
    assert res.values["c"] == 10
    assert res.artifacts["c"] == code


def test_function_nested_depend_global_right_order(execute):
    code = """def foo():
    def inner():
        return a
    return inner
a = 10
fn = foo()
a = 12
c = fn()
"""
    res = execute(code, artifacts=["c"])
    assert res.values["c"] == 12
    assert (
        res.artifacts["c"]
        == """def foo():
    def inner():
        return a
    return inner
fn = foo()
a = 12
c = fn()
"""
    )


def test_assign_global(execute):
    code = """def f():
    global a
    a = 1
f()
"""
    res = execute(code, artifacts=["a"])
    assert res.values["a"] == 1
    assert res.artifacts["a"] == code


def test_update_global(execute):
    code = """a = 10
def f():
    global a
    a = 1
f()
"""
    res = execute(code, artifacts=["a"])
    assert res.values["a"] == 1
    assert (
        res.artifacts["a"]
        == """def f():
    global a
    a = 1
f()
"""
    )


def test_imported_function(execute):
    code = """import math
a = 0
def my_function():
    global a
    a = math.factorial(5)
my_function()
"""
    res = execute(code, artifacts=["a"])
    assert res.values["a"] == 120
    assert (
        res.artifacts["a"]
        == """import math
def my_function():
    global a
    a = math.factorial(5)
my_function()
"""
    )
