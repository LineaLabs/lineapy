import pathlib

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
