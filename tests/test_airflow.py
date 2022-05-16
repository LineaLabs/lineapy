import pathlib
import subprocess

import pytest


def check_requirements_txt(t1: str, t2: str):
    return set(t1.split("\n")) == set(t2.split("\n"))


@pytest.mark.slow
@pytest.mark.parametrize(
    "artifact_names, dag_name, deps",
    [
        pytest.param(
            ["p value"],
            "sliced_housing_simple",
            {},
            id="sliced_housing_simple",
        ),
        pytest.param(
            ["p value", "y"],
            "sliced_housing_multiple",
            {},
            id="sliced_housing_multiple",
        ),
        pytest.param(
            ["p value", "y"],
            "sliced_housing_multiple_w_dependencies",
            {"y": {"p value"}},
            id="sliced_housing_multiple_w_dependencies",
        ),
    ],
)
def test_slice_airflow(artifact_names, dag_name, deps, airflow_plugin):
    """
    Test the slice produced by airflow plugin against a snapshot.
    """
    airflow_plugin.sliced_airflow_dag(
        artifact_names,
        dag_name,
        deps,
        output_dir="outputs/generated",
    )
    for file_endings in [".py", "_dag.py", "_Dockerfile", "_requirements.txt"]:
        path = pathlib.Path("outputs/generated/" + dag_name + file_endings)
        path_expected = pathlib.Path(
            "outputs/expected/" + dag_name + file_endings
        )
        if file_endings != "_requirements.txt":
            assert path.read_text() == path_expected.read_text()
        else:
            assert check_requirements_txt(
                path.read_text(), path_expected.read_text()
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
            "tests/outputs/expected/sliced_housing_simple_dag.py",
            "tests/outputs/expected/sliced_housing_simple.py",
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
        "airflow dags test sliced_housing_simple_dag 2020-10-19",
        capture=False,
        # Run in current root lineapy so that relative paths are accurate
        # cd=".",
    )
