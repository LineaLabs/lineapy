import pytest

from lineapy.utils.config import options
from lineapy.utils.utils import prettify

ARTIFACT_STORAGE_DIR = options.safe_get("artifact_storage_dir")


@pytest.mark.folder(ARTIFACT_STORAGE_DIR)
def test_save_returns_artifact(execute, move_folder):
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


@pytest.mark.folder(ARTIFACT_STORAGE_DIR)
def test_get_returns_artifact(execute, move_folder):
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


@pytest.mark.folder(ARTIFACT_STORAGE_DIR)
def test_get_version_zero(execute, move_folder):
    c = """import lineapy
x = 100
lineapy.save(x, 'x')
x = 200
lineapy.save(x, 'x')
x_ret = lineapy.get('x', version=0).get_value()
"""
    res = execute(c, snapshot=False)
    assert res.values["x_ret"] == 100


@pytest.mark.folder(ARTIFACT_STORAGE_DIR)
def test_save_different_session(execute, move_folder):
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


@pytest.mark.folder(ARTIFACT_STORAGE_DIR)
def test_save_twice(execute, move_folder):
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


@pytest.mark.folder(ARTIFACT_STORAGE_DIR)
def test_delete_artifact(execute, move_folder):
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


@pytest.mark.folder(ARTIFACT_STORAGE_DIR)
def test_delete_artifact_latest(execute, move_folder):
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


@pytest.mark.folder(ARTIFACT_STORAGE_DIR)
def test_delete_artifact_version_simple(execute, move_folder):
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


@pytest.mark.folder(ARTIFACT_STORAGE_DIR)
def test_delete_artifact_version(execute, move_folder):
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


@pytest.mark.folder(ARTIFACT_STORAGE_DIR)
def test_delete_artifact_version_complex(execute, move_folder):
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


@pytest.mark.folder(ARTIFACT_STORAGE_DIR)
def test_delete_artifact_all(execute, move_folder):
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
