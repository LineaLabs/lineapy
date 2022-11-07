import pytest

from lineapy.utils.utils import prettify

dask = pytest.importorskip("dask")


def test_dask_read_csv(execute):
    code = """import dask.dataframe as dd
import lineapy
df = dd.read_csv('tests/simple_data.csv')
"""
    res = execute(code, artifacts=["df"])
    assert res.values["df"]["a"].sum().compute() == 25


def test_dask_to_csv(execute):
    code = """import dask.dataframe as dd
import lineapy
df = dd.read_csv('tests/simple_data.csv')
dff = df.compute()
dff.to_csv('tests/simple_data_dask.csv')
lineapy.save(lineapy.file_system, 'simple_data_dask.csv')
"""
    res = execute(code, artifacts=["lineapy.file_system"])


def test_dask_compute_head(execute):
    code = """import dask.dataframe as dd
df = dd.read_csv('tests/simple_data.csv')
df.compute()
df.head()
"""
    res = execute(code, artifacts=["df"])
    assert res.artifacts["df"] == prettify(code)
