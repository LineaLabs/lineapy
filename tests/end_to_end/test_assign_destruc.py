def test_assignment_destructuring(execute):
    res = execute("a, b = (1, 2)")
    assert res.values["a"] == 1
    assert res.values["b"] == 2


# TODO - add test case for slice
#
# a, b = c
# a, *rest = c
# [a, b], *rest = c
# a = b = c
