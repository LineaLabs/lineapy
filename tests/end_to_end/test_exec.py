def test_mutate(execute):
    """
    Tests that calling a mutate function in an exec properly tracks it.
    """
    c = """x = []
if True:
    x.append(1)
"""
    res = execute(c, artifacts=["x"])
    assert res.artifacts["x"] == c
    assert res.values["x"] == [1]


def test_view_from_read(execute):
    """
    Tests adding a view in an exec will track it
    """
    c = """x = []
y = []
if True:
    x.append(y)
y.append(1)
"""
    res = execute(c, artifacts=["x"])
    assert res.artifacts["x"] == c
    assert res.values["x"] == [[1]]


def test_view_write(execute):
    """
    Tests that creating a new variable in an exec will mark it as a view
    of any read variables.
    """
    c = """x = []
if True:
    y = [x]
y.append(1)
"""
    res = execute(c, artifacts=["x"])
    assert res.artifacts["x"] == c
    assert res.values["y"] == [[], 1]
    assert res.values["x"] == []


def test_write_to_new_var(execute):
    """
    Tests that writing to a new variable wont require the old variable value.
    """
    c = """x = []
if True:
    x = []
    x.append(1)
"""
    res = execute(c, artifacts=["x"])
    assert (
        res.artifacts["x"]
        == """if True:
    x = []
    x.append(1)
"""
    )
    assert res.values["x"] == [1]


def test_overwritten_variable_view(execute):
    """
    Tests that the overwritten version of a variable will be a view
    of the old variable
    """
    c = """x = []
y = [x]
if True:
    x = [x]
x.append(1)
y.append(2)
"""
    res = execute(c, artifacts=["x", "y"])
    assert res.artifacts["x"] == c
    assert res.artifacts["y"] == c
    assert res.values["x"] == [[], 1]
    assert res.values["y"] == [[], 2]
