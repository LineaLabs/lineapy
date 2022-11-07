import pickle
from pathlib import Path

from lineapy.api.artifact_serializer import _try_write_to_pickle
from lineapy.api.models.linea_artifact import LineaArtifact
from lineapy.utils.config import options


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
    artifactorm = res.db.get_artifactorm_by_name("x")
    full_graph_artifact = LineaArtifact(
        db=res.db,
        _execution_id=artifactorm.execution_id,
        _node_id=artifactorm.node_id,
        _session_id=artifactorm.node.session_id,
        _version=artifactorm.version,
        name=artifactorm.name,
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


def test_write_to_pickle():
    _try_write_to_pickle(42, "test_pickle")
    pickle_path = (
        Path(options.safe_get("artifact_storage_dir")) / "test_pickle"
    )
    assert pickle_path.exists()

    with pickle_path.open("rb") as f:
        assert pickle.load(f) == 42
