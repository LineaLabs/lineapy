def test_assignment_destructuring(execute):
    res = execute("a, b = [1, 2]")
    assert res.values["a"] == 1
    assert res.values["b"] == 2


def test_assignment_destructuring_1(execute):
    res = execute("x=3\na, b, c, d, e, f = [1, 2, x, 4, 5, 6]")
    assert res.values["a"] == 1
    assert res.values["b"] == 2
    assert res.values["c"] == 3
    assert res.values["d"] == 4
    assert res.values["e"] == 5
    assert res.values["f"] == 6
    assert res.values["x"] == 3


# def test_assignment_destructuring_2(execute):
#     res = execute("a, *b, c = [1, 2, 3, 4]")
#     assert res.values["a"] == 1
#     # assert res.values["b"] == [2, 3]
#     assert res.values["c"] == 4


# def test_assignment_destructuring_basic(execute):
#     code = """a = [1,2,5]
# b, c, d = a
# """
#     res = execute(code)
#     assert res.values["b"] == 1
#     assert res.values["c"] == 2
#     assert res.values["d"] == 5
#

# def test_assignment_destructuring_slice(execute):
#     code = """import lineapy
# c = [1,2]
# a, b = c
# lineapy.save(a, "a")
# """
#     res = execute(code)
#     # assert res.slice("b") == "c = [1,2]\na, b = c\n"
#     assert res.values["a"] == 1
#     assert res.values["b"] == 2

# def test_assignment_destructuring_2(execute):
#     res = execute("c=3\na=b=c")
#     assert res.values["a"] == 3
#     assert res.values["b"] == 3
#     assert res.values["c"] == 3


# TODO - add test case for slice
#
# a, b = c
# a, *rest = c
# [a, b], *rest = c
# a = b = c
