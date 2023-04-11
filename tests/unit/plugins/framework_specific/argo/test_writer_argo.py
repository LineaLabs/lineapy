from pathlib import Path

import pytest

from tests.unit.plugins.framework_specific.workflow_helper import (
    workflow_file_generation_helper,
)


@pytest.mark.argo
@pytest.mark.slow
@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, workflow_name, dependencies, input_parameters",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "argo_workflow_a0_b0",
            {},
            [],
            id="argo_workflow_a0_b0",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "argo_workflow_a0_b0_dependencies",
            {"a0": {"b0"}},
            [],
            id="argo_workflow_a0_b0_dependencies",
        ),
        pytest.param(
            "simple",
            "",
            ["a", "b0"],
            "argo_workflow_a_b0_inputpar",
            {},
            ["b0"],
            id="argo_workflow_a_b0_inputpar",
        ),
        pytest.param(
            "simple_twovar",
            "",
            ["pn"],
            "argo_workflow_two_input_parameter",
            {},
            ["n", "p"],
            id="argo_workflow_two_input_parameter",
        ),
        pytest.param(
            "complex",
            "",
            ["f", "h"],
            "argo_complex_h",
            {},
            [],
            id="argo_complex_h",
        ),
        pytest.param(
            "housing",
            "",
            ["p value"],
            "argo_workflow_housing_simple",
            {},
            [],
            id="argo_workflow_housing_simple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "argo_workflow_housing_multiple",
            {},
            [],
            id="argo_workflow_housing_multiple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "argo_workflow_housing_w_dependencies",
            {"p value": {"y"}},
            [],
            id="argo_workflow_housing_w_dependencies",
        ),
        pytest.param(
            "simple",
            "linear",
            ["a", "linear_second", "linear_third"],
            "argo_hidden_session_dependencies",
            {"linear_third": {"a"}},
            [],
            id="argo_hidden_session_dependencies",
        ),
    ],
)
@pytest.mark.parametrize(
    "dag_config",
    [
        pytest.param(
            {"dag_flavor": "StepPerSession"},
            id="argo_workflow_step_per_session",
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
    Snapshot tests for Argo workflows.
    """

    workflow_file_generation_helper(
        tmp_path,
        linea_db,
        execute,
        input_script1,
        input_script2,
        artifact_list,
        "ARGO",
        workflow_name,
        dependencies,
        dag_config,
        input_parameters,
    )

    # Get list of files to compare
    file_endings = ["_module.py", "_requirements.txt", "_dag.py"]

    file_names = [workflow_name + file_suffix for file_suffix in file_endings]

    # Compare generated vs. expected
    for expected_file_name in file_names:
        path = Path(tmp_path, expected_file_name)
        generated = path.read_text()
        assert generated == snapshot
