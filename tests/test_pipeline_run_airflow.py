import subprocess

import pytest


@pytest.mark.airflow
@pytest.mark.slow
def test_run_airflow_dag(virtualenv, tmp_path):
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
            "tests/unit/plugins/expected/airflow_pipeline_housing_simple/airflow_pipeline_housing_simple_dag.py",
            "tests/unit/plugins/expected/airflow_pipeline_housing_simple/airflow_pipeline_housing_simple_module.py",
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
        "airflow dags test airflow_pipeline_housing_simple_dag 2020-10-19",
        capture=False,
        # Run in current root lineapy so that relative paths are accurate
        # cd=".",
    )
