from pathlib import Path

import pytest

from tests.unit.plugins.framework_specific.workflow_helper import (
    workflow_file_generation_helper,
)


@pytest.mark.ray
@pytest.mark.slow
@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, workflow_name, dependencies, input_parameters",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "ray_workflow_a0_b0",
            {},
            [],
            id="ray_workflow_a0_b0",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "ray_workflow_a0_b0_dependencies",
            {"a0": {"b0"}},
            [],
            id="ray_workflow_a0_b0_dependencies",
        ),
        pytest.param(
            "simple",
            "",
            ["a", "b0"],
            "ray_workflow_a_b0_inputpar",
            {},
            ["b0"],
            id="ray_workflow_a_b0_inputpar",
        ),
        pytest.param(
            "simple_twovar",
            "",
            ["pn"],
            "ray_workflow_two_input_parameter",
            {},
            ["n", "p"],
            id="ray_workflow_two_input_parameter",
        ),
        pytest.param(
            "complex",
            "",
            ["f", "h"],
            "ray_complex_h",
            {},
            [],
            id="ray_complex_h",
        ),
        pytest.param(
            "housing",
            "",
            ["p value"],
            "ray_workflow_housing_simple",
            {},
            [],
            id="ray_workflow_housing_simple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "ray_workflow_housing_multiple",
            {},
            [],
            id="ray_workflow_housing_multiple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "ray_workflow_housing_w_dependencies",
            {"p value": {"y"}},
            [],
            id="ray_workflow_housing_w_dependencies",
        ),
        pytest.param(
            "simple",
            "linear",
            ["a", "linear_second", "linear_third"],
            "ray_hidden_session_dependencies",
            {"linear_third": {"a"}},
            [],
            id="ray_hidden_session_dependencies",
        ),
    ],
)
@pytest.mark.parametrize(
    "dag_config",
    [
        pytest.param(
            {"dag_flavor": "TaskPerSession"},
            id="ray_workflow_task_per_session",
        ),
        pytest.param(
            {"dag_flavor": "TaskPerArtifact"},
            id="ray_workflow_task_per_artifact",
        ),
    ],
)
def test_workflow_generation(
    tmp_path,
    linea_db,
    execute,
    input_script1,
    input_script2,
    artifact_list,
    workflow_name,
    dependencies,
    dag_config,
    input_parameters,
    snapshot,
):
    """
    Snapshot tests for Ray workflows.
    """

    try:
        workflow_file_generation_helper(
            tmp_path,
            linea_db,
            execute,
            input_script1,
            input_script2,
            artifact_list,
            "RAY",
            workflow_name,
            dependencies,
            dag_config,
            input_parameters,
        )
    # Ray has few configurations that are not supported by the workflows API
    # ensure that these error out, using error message as snapshot
    except RuntimeError as e:
        assert snapshot == repr(e)
        return

    # Get list of files to compare
    file_endings = ["_module.py", "_requirements.txt", "_dag.py"]

    file_names = [workflow_name + file_suffix for file_suffix in file_endings]

    # Compare generated vs. expected
    for expected_file_name in file_names:
        path = Path(tmp_path, expected_file_name)
        generated = path.read_text()
        assert generated == snapshot
