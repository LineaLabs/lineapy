def test_variable(execute):
    res = execute("a = 1")
    assert res.values["a"] == 1


def test_compareops(execute):
    execute("b = 1 < 2 < 3\nassert b")


def test_binops(execute):
    execute("b = 1 + 2\nassert b == 3")


def test_subscript(execute):
    execute("ls = [1,2]\nassert ls[0] == 1")
