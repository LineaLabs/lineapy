from lineapy.utils.utils import prettify


def test_user_defined_decorator(execute):
    code = """x=[]
def append1(func):
    def wrapper():
        func()
        x.append(1)

    return wrapper


@append1
def append2():
    x.append(2)

append2()
"""
    res = execute(code, artifacts=["x"])
    assert len(res.values["x"]) == 2
    assert res.values["x"][0] == 2 and res.values["x"][1] == 1
    assert res.artifacts["x"] == prettify(code)


def test_functools_decorator(execute):
    code = """from functools import lru_cache
@lru_cache
def f():
    return 1

x = f()
"""
    res = execute(code, artifacts=["x"])
    assert res.values["x"] == 1
    assert res.artifacts["x"] == prettify(code)
