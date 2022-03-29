import pathlib
import subprocess

import pytest


@pytest.mark.slow
def test_slice_airflow(airflow_plugin):
    """
    Test the slice produced by airflow plugin against a snapshot.
    """
    airflow_plugin.sliced_airflow_dag(
        ["p value"],
        "sliced_housing_simple",
        "",
        output_dir="outputs/generated/simple",
    )
    for file_endings in [".py", "_dag.py", "_Dockerfile", "_requirements.txt"]:
        path = pathlib.Path(
            "outputs/generated/simple/sliced_housing_simple" + file_endings
        )
        path_expected = pathlib.Path(
            "outputs/expected/simple/sliced_housing_simple" + file_endings
        )
        assert path.read_text() == path_expected.read_text()


@pytest.mark.slow
def test_multiple_slices_airflow(python_snapshot, airflow_plugin):
    """
    Test producing ariflow DAG slicng several artifacts.
    """
    airflow_plugin.sliced_airflow_dag(
        ["p value", "y"],
        "sliced_housing_multiple",
        "",
        output_dir="outputs/generated/multiple",
    )
    for file_endings in [".py", "_dag.py", "_Dockerfile", "_requirements.txt"]:
        path = pathlib.Path(
            "outputs/generated/multiple/sliced_housing_multiple" + file_endings
        )
        path_expected = pathlib.Path(
            "outputs/expected/multiple/sliced_housing_multiple" + file_endings
        )
        assert path.read_text() == path_expected.read_text()


@pytest.mark.slow
def test_multiple_slices_airflow_with_task_dependencies(
    python_snapshot, airflow_plugin
):
    """
    Test producing and ariflow DAG slicng several artifacts with task dependencies.
    """
    airflow_plugin.sliced_airflow_dag(
        ["p value", "y"],
        "sliced_housing_multiple_w_dependencies",
        "'p value' >> 'y'",
        output_dir="outputs/generated/multiple_w_dependencies",
    )

    for file_endings in [".py", "_dag.py", "_Dockerfile", "_requirements.txt"]:
        path = pathlib.Path(
            "outputs/generated/multiple_w_dependencies/sliced_housing_multiple_w_dependencies"
            + file_endings
        )
        path_expected = pathlib.Path(
            "outputs/expected/multiple_w_dependencies/sliced_housing_multiple_w_dependencies"
            + file_endings
        )
        assert path.read_text() == path_expected.read_text()


@pytest.mark.airflow
@pytest.mark.slow
@pytest.mark.skip
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
            "tests/entrypoints/outputs/generated/simple/sliced_housing_simple_dag.py",
            "tests/entrypoints/outputs/generated/simple/sliced_housing_simple.py",
            "tests/entrypoints/outputs/generated/simple/ames_train_cleaned.csv",
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
        "airflow dags test sliced_housing_simple_dag 2020-10-19",
        capture=False,
        # Run in current root lineapy so that relative paths are accurate
        # cd=".",
    )