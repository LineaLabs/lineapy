import pathlib

import pytest


def check_requirements_txt(t1: str, t2: str):
    return set(t1.split("\n")) == set(t2.split("\n"))


@pytest.mark.slow
def test_slice_pythonscript(script_plugin):
    """
    Test the slice produced by script plugin against a snapshot.
    """
    script_plugin.sliced_pipeline_dag(
        ["p value"],
        "sliced_housing_simple",
        [],
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
def test_multiple_slices_pythonscript(python_snapshot, script_plugin):
    """
    Test producing ariflow DAG slicng several artifacts.
    """
    script_plugin.sliced_pipeline_dag(
        ["p value", "y"],
        "sliced_housing_multiple",
        {},
        output_dir="outputs/generated",
    )
    for file_endings in [
        ".py",
        "_script_dag.py",
        "_Dockerfile",
        "_requirements.txt",
    ]:
        path = pathlib.Path(
            "outputs/generated/sliced_housing_multiple" + file_endings
        )
        path_expected = pathlib.Path(
            "outputs/expected/sliced_housing_multiple" + file_endings
        )
        if file_endings != "_requirements.txt":
            assert path.read_text() == path_expected.read_text()
        else:
            assert check_requirements_txt(
                path.read_text(), path_expected.read_text()
            )


@pytest.mark.slow
def test_multiple_slices_airflow_with_task_dependencies(
    python_snapshot, script_plugin
):
    """
    Test producing and ariflow DAG slicng several artifacts with task dependencies.
    """
    script_plugin.sliced_pipeline_dag(
        ["p value", "y"],
        "sliced_housing_multiple_w_dependencies",
        {"y": {"p value"}},
        output_dir="outputs/generated",
    )

    for file_endings in [
        ".py",
        "_script_dag.py",
        "_Dockerfile",
        "_requirements.txt",
    ]:
        path = pathlib.Path(
            "outputs/generated/sliced_housing_multiple_w_dependencies"
            + file_endings
        )
        path_expected = pathlib.Path(
            "outputs/expected/sliced_housing_multiple_w_dependencies"
            + file_endings
        )
        if file_endings != "_requirements.txt":
            assert path.read_text() == path_expected.read_text()
        else:
            assert check_requirements_txt(
                path.read_text(), path_expected.read_text()
            )
