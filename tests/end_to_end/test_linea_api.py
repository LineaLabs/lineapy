import pytest

from lineapy.utils.config import options
from lineapy.utils.utils import prettify

ARTIFACT_STORAGE_DIR = options.safe_get("artifact_storage_dir")


def test_save_returns_artifact(execute):
    c = """import lineapy
x = 1
res = lineapy.save(x, "x")
slice = res.get_code()
value = res.get_value()
"""

    res = execute(c, snapshot=False)
    assert (
        res.artifacts["x"]
        == """x = 1
"""
    )
    assert res.values["slice"] == res.artifacts["x"]
    assert res.values["value"] == res.values["x"]


def test_get_returns_artifact(execute):
    c = """import lineapy
x = 1
lineapy.save(x, "x")

res = lineapy.get("x")
y = res.get_value() + 1
lineapy.save(y, "y")
"""

    res = execute(c, snapshot=False)
    assert (
        res.artifacts["x"]
        == """x = 1
"""
    )
    assert res.artifacts["y"] == prettify(
        """import lineapy
res = lineapy.get("x")
y = res.get_value() + 1
"""
    )
    assert res.values["y"] == 2


def test_get_version_zero(execute):
    c = """import lineapy
x = 100
lineapy.save(x, 'x')
x = 200
lineapy.save(x, 'x')
x_ret = lineapy.get('x', version=0).get_value()
"""
    res = execute(c, snapshot=False)
    assert res.values["x_ret"] == 100


def test_save_different_session(execute):
    execute("import lineapy\nlineapy.save(10, 'x')", snapshot=False)
    c = """import lineapy
y = lineapy.get('x').get_value() + 10
lineapy.save(y, 'y')
"""
    res = execute(c, snapshot=False)
    assert res.values["y"] == 20
    assert res.artifacts["y"] == prettify(
        """import lineapy
y = lineapy.get('x').get_value() + 10
"""
    )


def test_save_twice(execute):
    res = execute(
        """import lineapy
x = 100
lineapy.save(x, 'x')
lineapy.save(x, 'x')
y = 100
lineapy.save(y, 'y')
""",
        snapshot=False,
    )
    assert res.values["x"] == 100
    assert res.artifacts["x"] == "x = 100\n"

    assert res.values["y"] == 100
    assert res.artifacts["y"] == "y = 100\n"


def test_delete_artifact(execute):
    res = execute(
        """import lineapy
x = 100
lineapy.save(x, 'x')
lineapy.delete('x', version='latest')
""",
        snapshot=False,
    )

    with pytest.raises(KeyError):
        assert res.artifacts["x"]


def test_delete_artifact_latest(execute):
    res = execute(
        """import lineapy
x = 100
lineapy.save(x, 'x')
x = 200
lineapy.save(x, 'x')
lineapy.delete('x', version='latest')

store = lineapy.artifact_store()
versions = [x._version for x in store.artifacts if x.name=='x']
num_versions = len(versions)
""",
        snapshot=False,
    )

    assert res.artifacts["x"] == "x = 100\n"
    assert res.values["num_versions"] == 1


def test_delete_artifact_version_simple(execute):
    res = execute(
        """import lineapy
x = 100
lineapy.save(x, 'x')
lineapy.delete('x', version=0)
""",
        snapshot=False,
    )

    with pytest.raises(KeyError):
        assert res.artifacts["x"]


def test_delete_artifact_version(execute):
    res = execute(
        """import lineapy
x = 100
lineapy.save(x, 'x')
x = 200
lineapy.save(x, 'x')
lineapy.delete('x', version=1)

store = lineapy.artifact_store()
versions = [x._version for x in store.artifacts if x.name=='x']
num_versions = len(versions)
x_retrieve = lineapy.get('x').get_value()

""",
        snapshot=False,
    )

    assert res.values["num_versions"] == 1
    assert res.values["x_retrieve"] == 100


def test_delete_artifact_version_complex(execute):
    res = execute(
        """import lineapy
x = 100
lineapy.save(x, 'x')
x = 200
lineapy.save(x, 'x')
x = 300
lineapy.save(x, 'x')

# We want to Delete version 1, but the code is executed twice in testing, causing no version 1 to be deleted in second execution
lineapy.delete('x', version=sorted([x._version for x in lineapy.artifact_store().artifacts if x.name=='x'])[-2])

num_versions = len([x._version for x in lineapy.artifact_store().artifacts if x.name=='x'])
x_retrieve = lineapy.get('x').get_value()
""",
        snapshot=False,
    )

    assert res.values["num_versions"] == 2
    assert res.values["x_retrieve"] == 300


def test_delete_artifact_all(execute):
    res = execute(
        """import lineapy
x = 100
lineapy.save(x, 'x')
x = 200
lineapy.save(x, 'x')
x = 300
lineapy.save(x, 'x')
lineapy.delete('x', version='all')

store = lineapy.artifact_store()
versions = [x._version for x in store.artifacts if x.name=='x']
num_versions = len(versions)


""",
        snapshot=False,
    )

    assert res.values["num_versions"] == 0
    with pytest.raises(KeyError):
        assert res.artifacts["x"]


def test_pipeline_simple(execute):

    c = """import lineapy
lineapy.create_pipeline([], "x", persist=True)
x = lineapy.get_pipeline("x")"""
    res = execute(c, snapshot=False)
    assert res.values["x"].name == "x"


def test_pipeline_complex(execute):
    c = """import lineapy
a = 10
b = 20
lineapy.save(a, "a")
lineapy.save(b, "b")
lineapy.create_pipeline(["a", "b"], "x", persist=True)
x = lineapy.get_pipeline("x")"""
    res = execute(c, snapshot=False)
    assert res.values["x"].name == "x"
    arts = res.values["x"].artifact_names
    assert len(arts) == 2
    assert "a" in arts
    assert "b" in arts


def test_two_pipelines_simple(execute):

    c = """import lineapy
a = 10
b = 20
lineapy.save(a, "a")
lineapy.save(b, "b")
lineapy.create_pipeline(["a"], "x", persist=True)
lineapy.create_pipeline(["b"], "y", persist=True)
x = lineapy.get_pipeline("x")
y = lineapy.get_pipeline("y")"""
    res = execute(c, snapshot=False)
    assert res.values["x"].name == "x"
    assert res.values["y"].name == "y"
    arts_x = res.values["x"].artifact_names
    assert len(arts_x) == 1
    assert "a" in arts_x
    arts_y = res.values["y"].artifact_names
    assert len(arts_y) == 1
    assert "b" in arts_y


def test_two_pipelines_complex(execute):

    c = """import lineapy
a = 10
b = 20
lineapy.save(a, "a")
lineapy.save(b, "b")
lineapy.create_pipeline(["a", "b"], "x", persist=True)
lineapy.create_pipeline(["b"], "y", persist=True)
x = lineapy.get_pipeline("x")
y = lineapy.get_pipeline("y")"""
    res = execute(c, snapshot=False)
    assert res.values["x"].name == "x"
    assert res.values["y"].name == "y"
    arts_x = res.values["x"].artifact_names
    assert len(arts_x) == 2
    assert "a" in arts_x
    assert "b" in arts_x
    arts_y = res.values["y"].artifact_names
    assert len(arts_y) == 1
    assert "b" in arts_y


def test_pipeline_deps_simple(execute):
    c = """import lineapy
a = 10
b = 20
lineapy.save(a, "a")
lineapy.save(b, "b")
dep = {"a": {"b"}}
lineapy.create_pipeline(["a", "b"], "x", persist=True, dependencies=dep)
x = lineapy.get_pipeline("x")"""
    res = execute(c, snapshot=False)
    assert res.values["x"].name == "x"
    deps = res.values["x"].dependencies
    assert len(deps) == 1
    assert len(deps["a"]) == 1
    assert "b" in deps["a"]


def test_pipeline_deps_complex(execute):
    c = """import lineapy
a = 10
b = 20
c = 30
lineapy.save(a, "a")
lineapy.save(b, "b")
lineapy.save(c, "c")
dep_x = {"a": {"b"}}
dep_y = {"b": {"c", "a"}}
lineapy.create_pipeline(["a", "b", "c"], "x", persist=True, dependencies=dep_x)
lineapy.create_pipeline(["a", "b", "c"], "y", persist=True, dependencies=dep_y)
x = lineapy.get_pipeline("x")
y = lineapy.get_pipeline("y")"""
    res = execute(c, snapshot=False)
    assert res.values["x"].name == "x"
    assert res.values["y"].name == "y"
    dep_x = res.values["x"].dependencies
    assert len(dep_x) == 1
    assert len(dep_x["a"]) == 1
    assert "b" in dep_x["a"]
    dep_y = res.values["y"].dependencies
    assert len(dep_y) == 1
    assert len(dep_y["b"]) == 2
    assert "c" in dep_y["b"]
    assert "a" in dep_y["b"]
