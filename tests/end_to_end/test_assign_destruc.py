def test_assignment_destructuring_basic_tuple(execute):
    res = execute("a, b = (1, 2)")
    assert res.values["a"] == 1
    assert res.values["b"] == 2


def test_assignment_destructuring_basic(execute):
    res = execute("a, b , c = [1, 2, 3]")
    assert res.values["a"] == 1
    assert res.values["b"] == 2
    assert res.values["c"] == 3


def test_assignment_destructuring_with_reference(execute):
    code = """a = [1,2,5]
b, c, d = a
"""
    res = execute(code)
    assert res.values["a"] == [1, 2, 5]
    assert res.values["b"] == 1
    assert res.values["c"] == 2
    assert res.values["d"] == 5


def test_assignment_destructuring_with_alias(execute):
    res = execute("a=3\nb, c, d = [1, 2, a]")
    assert res.values["a"] == 3
    assert res.values["b"] == 1
    assert res.values["c"] == 2
    assert res.values["d"] == 3


def test_assignment_destructuring_starred_basic(execute):
    res = execute("a, *b, c = [1, 2, 3]")
    assert res.values["a"] == 1
    assert res.values["b"] == [2]
    assert res.values["c"] == 3


def test_assignment_destructuring_starred_list(execute):
    res = execute("a, *b, c = [1, 2, 3, 4]")
    assert res.values["a"] == 1
    assert res.values["b"] == [2, 3]
    assert res.values["c"] == 4


def test_assignment_destructuring_starred_basic_no_after(execute):
    res = execute("a, *b = [1, 2]")
    assert res.values["a"] == 1
    assert res.values["b"] == [2]


def test_assignment_destructuring_starred_list_no_after(execute):
    res = execute("a, *b = [1, 2, 3]")
    assert res.values["a"] == 1
    assert res.values["b"] == [2, 3]


def test_assignment_destructuring_starred_basic_no_before(execute):
    res = execute("*a, b = [1, 2]")
    assert res.values["a"] == [1]
    assert res.values["b"] == 2


def test_assignment_destructuring_starred_list_no_before(execute):
    res = execute("*a, b = [1, 2, 3]")
    assert res.values["a"] == [1, 2]
    assert res.values["b"] == 3


def test_assignment_destructuring_complex(execute):
    # [a, b], *rest = c
    res = execute("c = [[1, 2], 3]\n[a, b], *rest = c")
    assert res.values["a"] == 1
    assert res.values["b"] == 2
    assert res.values["rest"] == [3]


def test_assignment_destructuring_slice(execute):
    code = """import lineapy
c = [1,2]
a, b = c
lineapy.save(a, "a")
lineapy.save(b, "b")
lineapy.save(c, "c")
"""
    res = execute(code)
    assert res.values["a"] == 1
    assert res.values["b"] == 2
    assert res.values["c"] == [1, 2]
    assert res.slice("a") == "c = [1,2]\na, b = c\n"
    assert res.slice("b") == "c = [1,2]\na, b = c\n"
    assert res.slice("c") == "c = [1,2]\n"


def test_assignment_destructuring_starred_slice(execute):
    code = """import lineapy
c = [1,2,3]
a, *b = c
lineapy.save(a, "a")
lineapy.save(b, "b")
lineapy.save(c, "c")
"""
    res = execute(code)
    assert res.values["a"] == 1
    assert res.values["b"] == [2, 3]
    assert res.values["c"] == [1, 2, 3]
    assert res.slice("a") == "c = [1,2,3]\na, *b = c\n"
    assert res.slice("b") == "c = [1,2,3]\na, *b = c\n"
    assert res.slice("c") == "c = [1,2,3]\n"
