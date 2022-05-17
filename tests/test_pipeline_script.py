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
def test_slice_pythonscript(artifact_names, dag_name, deps, script_plugin):
    """
    Test the slice produced by script plugin against a snapshot.
    """
    script_plugin.sliced_pipeline_dag(
        artifact_names,
        dag_name,
        deps,
        output_dir="outputs/generated",
    )
    for file_endings in [
        ".py",
        "_script_dag.py",
        "_Dockerfile",
        "_requirements.txt",
    ]:
        path = pathlib.Path(
            "outputs/generated/sliced_housing_simple" + file_endings
        )
        path_expected = pathlib.Path(
            "outputs/expected/sliced_housing_simple" + file_endings
        )
        if file_endings != "_requirements.txt":
            assert path.read_text() == path_expected.read_text()
        else:
            assert check_requirements_txt(
                path.read_text(), path_expected.read_text()
            )


@pytest.mark.slow
def test_run_script_dag(virtualenv, tmp_path):
    """
    Verifies that the dags we produce  CLI command produces a working Airflow DAG
    by running the DAG locally.

    Depends on snapshot being available from previous test.
    """

    # Copy the dag and the data
    # NOTE: We can't leave them in the tests folder, since there are other
    # files in there that airflow will attempt to import, and fail, since
    # those dependencies are not in the virtualenv.
    subprocess.check_call(
        [
            "cp",
            "-f",
            "tests/outputs/expected/sliced_housing_multiple_script_dag.py",
            "tests/outputs/expected/sliced_housing_multiple.py",
            "tests/ames_train_cleaned.csv",
            str(tmp_path),
        ]
    )

    # Run airflow in new virtual env so we don't end up with version conflicts
    # with lineapy deps
    # https://github.com/man-group/pytest-plugins/tree/master/pytest-virtualenv#installing-packages
    virtualenv.run(
        "pip install pandas scikit-learn", capture=False, cd=str(tmp_path)
    )

    # Set the airflow home for subsequent calls
    # virtualenv.env["AIRFLOW_HOME"] = str(airflow_home)
    # We create a new DB for airflow for testing, so it's reproducible
    # virtualenv.run("airflow db init", capture=False)
    virtualenv.run(
        "python sliced_housing_multiple_script_dag.py",
        capture=False,
        # Run in current root lineapy so that relative paths are accurate
        cd=str(tmp_path),
    )
