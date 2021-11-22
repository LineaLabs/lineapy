import pytest

CODE = """def func(a,b):
    return a+b

args = {'a':1, 'b':2}
ret = func(**args)
"""

CODE2 = """name="marcelo"
it=iter(name)
print(next(it))
print(*it)
"""


@pytest.mark.xfail
def test_starred_executes(execute):
    ret = execute(CODE)
    assert ret == 3


@pytest.mark.xfail
def test_starred2_executes(execute):
    # should execute without failures
    ret = execute(CODE2)
    assert True
