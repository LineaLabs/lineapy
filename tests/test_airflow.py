import pathlib
import subprocess

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


@pytest.mark.airflow
@pytest.mark.slow
def test_run_airflow(virtualenv, tmp_path):
    """
    Verifies that the "--airflow" CLI command produces a working Airflow DAG
    by running the DAG locally.

    Depends on snapshot being available from previous test.
    """
    airflow_home = tmp_path / "airflow"
    airflow_home.mkdir()
    dags_home = airflow_home / "dags"
    dags_home.mkdir()

    # Copy the dag and the data
    # NOTE: We can't leave them in the tests folder, since there are other
    # files in there that airflow will attempt to import, and fail, since
    # those dependencies are not in the virtualenv.
    subprocess.check_call(
        [
            "cp",
            "-f",
            "tests/__snapshots__/test_airflow/test_slice_airflow.py",
            "tests/ames_train_cleaned.csv",
            str(dags_home),
        ]
    )

    # TODO Start a local airflow server and test that the DAG runs successfully in it
