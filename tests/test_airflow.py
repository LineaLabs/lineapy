import pathlib

import pytest


@pytest.mark.slow
def test_slice_airflow(python_snapshot, airflow_plugin):
    """
    Test the slice produced by airflow plugin against a snapshot.
    """
    airflow_plugin.sliced_airflow_dag(["p value"], "sliced_housing_dag", "")
    assert python_snapshot == pathlib.Path("sliced_housing_dag.py").read_text()


@pytest.mark.slow
def test_multiple_slices_airflow(python_snapshot, airflow_plugin):
    """
    Test producing ariflow DAG slicng several artifacts.
    """
    airflow_plugin.sliced_airflow_dag(
        ["p value", "y"], "sliced_housing_dag", ""
    )
    assert python_snapshot == pathlib.Path("sliced_housing_dag.py").read_text()


@pytest.mark.slow
def test_multiple_slices_airflow_with_task_dependencies(
    python_snapshot, airflow_plugin
):
    """
    Test producing and ariflow DAG slicng several artifacts with task dependencies.
    """
    airflow_plugin.sliced_airflow_dag(
        ["p value", "y"],
        "sliced_housing_dag",
        "'p value' >> 'y'",
    )
    assert python_snapshot == pathlib.Path("sliced_housing_dag.py").read_text()
