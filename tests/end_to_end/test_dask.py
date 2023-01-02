import pytest

from lineapy.utils.utils import prettify

dask = pytest.importorskip("dask")


def test_dask_read_csv(execute):
    code = """import dask.dataframe as dd
df = dd.read_csv('tests/simple_data.csv')
"""
    res = execute(code, artifacts=["df"])
    assert res.values["df"]["a"].sum().compute() == 25


def test_dask_to_csv(execute):
    code = """import dask.dataframe as dd
df = dd.read_csv('tests/simple_data.csv')
df.to_csv('tests/simple_data_dask.csv')
"""
    res = execute(code, artifacts=["lineapy.file_system"])
    assert res.artifacts["lineapy.file_system"] == prettify(code)


def test_dask_pop(execute):
    code = """import dask.dataframe as dd
df = dd.read_csv('tests/simple_data.csv')
df.pop('a')
"""
    res = execute(code, artifacts=["df"])
    assert res.values["df"].columns == ["b"]
    assert res.artifacts["df"] == prettify(code)
