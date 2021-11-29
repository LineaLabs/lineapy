import pytest


@pytest.mark.xfail
def test_starred_executes(execute):
    CODE = """def func(a,b):
    return a+b

args = {'a':1, 'b':2}
ret = func(**args)
"""
    ret = execute(CODE)
    assert ret == 3


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
