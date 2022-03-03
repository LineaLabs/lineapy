def test_assignment_destructuring(execute):
    res = execute("a, b = (1, 2)")
    assert res.values["a"] == 1
    assert res.values["b"] == 2


def test_assignment_destructuring_basic(execute):
    code = """c = [1,2]
a, b = c
lineapy.save(a, "a")
"""
    res = execute(code)
    assert res.slice("a") == "c = [1,2]\na, b = c\n"
    assert res.values["a"] == 1
    assert res.values["b"] == 2


# TODO - add test case for slice
#
# a, b = c
# a, *rest = c
# [a, b], *rest = c
# a = b = c
