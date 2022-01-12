import subprocess

import pytest

from lineapy.plugins.airflow import sliced_aiflow_dag


@pytest.mark.slow
def test_slice_airflow(python_snapshot, housing_tracer):
    """
    Test the slice produced by airflow against a snapshot.
    """
    assert python_snapshot == sliced_aiflow_dag(
        housing_tracer, ["p value"], "sliced_housing_dag", ""
    )


@pytest.mark.slow
def test_multiple_slices_airflow(python_snapshot, housing_tracer):
    """
    Test producing and ariflow DAG slicng several artifacts.
    """
    assert python_snapshot == sliced_aiflow_dag(
        housing_tracer, ["p value", "y"], "sliced_housing_dag", ""
    )


@pytest.mark.slow
def test_multiple_slices_airflow_with_task_dependencies(
    python_snapshot, housing_tracer
):
    """
    Test producing and ariflow DAG slicng several artifacts with task dependencies.
    """
    assert python_snapshot == sliced_aiflow_dag(
        housing_tracer,
        ["p value", "y"],
        "sliced_housing_dag",
        "'p value' >> 'y'",
    )


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

    # Run airflow in new virtual env so we don't end up with version conflicts
    # with lineapy deps
    # https://github.com/man-group/pytest-plugins/tree/master/pytest-virtualenv#installing-packages
    virtualenv.run(
        "pip install -r airflow-requirements.txt", capture=False, cd="."
    )

    # Set the airflow home for subsequent calls
    virtualenv.env["AIRFLOW_HOME"] = str(airflow_home)
    # We create a new DB for airflow for testing, so it's reproducible
    virtualenv.run("airflow db init", capture=False)
    virtualenv.run(
        "airflow dags test sliced_housing_dag_dag 2020-10-19",
        capture=False,
        # Run in current root lineapy so that relative paths are accurate
        cd=".",
    )
