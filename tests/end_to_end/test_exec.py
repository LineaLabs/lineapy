from pytest import mark

import lineapy.graph_reader.program_slice as ps
from lineapy.execution.executor import Executor


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
    artifact_id = res.db.get_artifact_by_name("x").node_id
    # slice_nodes = res.graph.get_ancestors(artifact_id)
    # slice_graph = res.graph.get_subgraph(slice_nodes)
    slice_graph = ps.get_slice_graph(res.graph, [artifact_id])
    res_slice = Executor(res.db, globals())
    res_slice.execute_graph(slice_graph)
    assert res_slice.get_value(artifact_id) == res.values["x"]

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


def test_view_from_loop(execute):
    """
    Verifies that a view is added when looping over a variable that is mutable
    """
    c = """xs = [[]]
for x in xs:
    pass
x.append(10)
"""
    res = execute(c, artifacts=["x", "xs"])
    assert res.artifacts["xs"] == c
    assert res.artifacts["x"] == c


@mark.xfail()
def test_loop_no_mutate(execute):
    """
    Verifies that a loop which does not mutate, will not include a mutation
    """
    c = """xs = [[]]
for x in xs:
    pass
"""
    res = execute(c, artifacts=["x", "xs"])
    assert (
        res.artifacts["xs"]
        == """xs = [[]]
"""
    )
    assert res.artifacts["x"] == c


def test_loop_mutate(execute):
    """
    Verifies that a loop which does mutate, will include a mutation
    """
    c = """xs = [[]]
for x in xs:
    x.append(10)
"""
    res = execute(c, artifacts=["x", "xs"])
    assert res.artifacts["xs"] == c
    assert res.artifacts["x"] == c
