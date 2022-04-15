from lineapy.graph_reader.apis import LineaArtifact


def test_execute_slice(execute):
    """
    Tests that executing a slice of a graph yields the same result as executing the graph
    """
    c = """x = []
if True:
    x = []
    x.append(1)
"""
    res = execute(c, artifacts=["x"], snapshot=False)
    artifact = res.db.get_artifact_by_name("x")
    full_graph_artifact = LineaArtifact(
        db=res.db,
        _execution_id=artifact.execution_id,
        _node_id=artifact.node_id,
        _session_id=artifact.node.session_id,
        _version=artifact.version,
        date_created=artifact.date_created,
        name=artifact.name,
    )

    slice_graph_artifact_res = full_graph_artifact.execute()
    assert slice_graph_artifact_res == res.values["x"]
    assert (
        res.artifacts["x"]
        == """if True:
    x = []
    x.append(1)
"""
    )
    assert res.values["x"] == [1]
