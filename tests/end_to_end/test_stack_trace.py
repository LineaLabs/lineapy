import pytest


@pytest.mark.xfail
def test_basic_exception(execute):
    def MyException(Exception):
        pass

    code = """def divide_me(a):
    return a/0
x = divide_me(1)
"""
    with pytest.raises(Exception) as e:
        res = execute(code)
    print(e.traceback)
    # assert e.traceback == ""

@pytest.mark.xfail
def test_syntax_error(execute):
    code = """
a = 10
a+++
"""
    with pytest.raises(Exception) as e:
        res = execute(code)
    print(e)
