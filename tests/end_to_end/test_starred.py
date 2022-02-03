import pytest


def test_starred_executes(execute):
    CODE = """def func(a,b):
    return a+b

args = {'a':1, 'b':2}
ret = func(**args)
"""
    ret = execute(CODE)
    assert ret.values["ret"] == 3


def test_starred2_executes(execute):
    CODE2 = """name="marcelo"
it=iter(name)
print(next(it))
print(*it)
"""
    # should execute without failures
    ret = execute(CODE2)
    assert True


def test_starred_in_func_executes(execute):
    CODE = """def func(*args):
    return [m for m in args]

name = "myname"
x = func(*name)
"""
    ret = execute(CODE)
    assert ret.values["x"] == ["m", "y", "n", "a", "m", "e"]


def test_star_w_string(execute):
    CODE = """def func(*args):
    return [m for m in args]
x=func(*"myname")
"""
    ret = execute(CODE)
    assert ret.values["x"] == ["m", "y", "n", "a", "m", "e"]


def test_starred_w_iterator_executes(execute):
    CODE = """def func(*args):
    retobv = (m for m in args)
    return list(retobv)

name = "myname"
it = iter(name)
print(next(it))
x = func(*it)
"""
    ret = execute(CODE)
    assert ret.values["x"] == ["y", "n", "a", "m", "e"]


@pytest.mark.xfail(
    reason="in some cases where return value is a generator, multiple assign calls are not supported"
)
def test_starred_w_zip(execute):
    CODE = """def func():
    for i in range(3):
        for j in range(3):
            yield (i,j), 10

ind, patch = zip(*func())"""

    ret = execute(CODE)
    assert ret.values["ind"] == (
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2),
    )
    assert ret.values["patch"] == (10, 10, 10, 10, 10, 10, 10, 10, 10)
