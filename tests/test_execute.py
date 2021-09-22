def test_variable(execute):
    res = execute("a = 1")
    assert res.values["a"] == 1


def test_compareops(execute):
    execute(
        """
b = 1 < 2 < 3
assert b
"""
    )


def test_binops(execute):
    execute(
        """
b = 1 + 2
assert b == 3
"""
    )


def test_subscript(execute):
    execute(
        """
ls = [1,2]
assert ls[0] == 1
"""
    )


def test_simple_with_variable_argument_and_print(execute):
    res = execute(
        """
a = abs(-11)
b = min(a, 10)
print(b)
"""
    )
    assert res.stdout == "10\n"
