import pytest
from lineapy.utils.utils import prettify


def test_save_returns_artifact(execute):
    c = """import lineapy
x = 1
res = lineapy.save(x, "x")
slice = res.get_code()
value = res.get_value()
"""

    res = execute(c)
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

    res = execute(c)
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


def test_save_different_session(execute):
    execute("import lineapy\nlineapy.save(10, 'x')")
    c = """import lineapy
y = lineapy.get('x').get_value() + 10
lineapy.save(y, 'y')
"""
    res = execute(c)
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
"""
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
lineapy.delete('x')
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
lineapy.delete('x')

catalog = lineapy.catalog()
versions = [x._version for x in catalog.artifacts if x.name=='x']
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


@pytest.mark.xfail(reason="There might be a bug with artifact versions")
def test_delete_artifact_version(execute):
    res = execute(
        """import lineapy
x = 100
lineapy.save(x, 'x')
x = 200
lineapy.save(x, 'x')
lineapy.delete('x', version=1)

catalog = lineapy.catalog()
versions = [x._version for x in catalog.artifacts if x.name=='x']
num_versions = len(versions)


""",
        snapshot=False,
    )

    assert res.values["num_versions"] == 1
    assert res.artifacts["x"] == "x = 100\n"


@pytest.mark.xfail(reason="There might be a bug with artifact versions")
def test_delete_artifact_version_complex(execute):
    res = execute(
        """import lineapy
x = 100
lineapy.save(x, 'x')
x = 200
lineapy.save(x, 'x')
x = 300
lineapy.save(x, 'x')
lineapy.delete('x', version=1)

catalog = lineapy.catalog()
versions = [x._version for x in catalog.artifacts if x.name=='x']
num_versions = len(versions)


""",
        snapshot=False,
    )

    assert res.values["num_versions"] == 2
    assert res.artifacts["x"] == "x = 300\n"
