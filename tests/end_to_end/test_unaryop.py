def test_sub(execute):
    res = execute("x = 1\ny=-x")
    assert res.values["y"] == -1


def test_add(execute):
    """
    Weird test case from https://stackoverflow.com/a/16819334/907060
    """
    execute(
        """from decimal import Decimal
obj = Decimal('3.1415926535897932384626433832795028841971')
assert +obj != obj"""
    )


def test_invert(execute):
    """
    https://stackoverflow.com/q/7278779/907060
    """
    res = execute("a = 1\nb=~a")
    assert res.values["b"] == -2


def test_not(execute):
    res = execute("a = 1\nb=not a")
    assert res.values["b"] is False
