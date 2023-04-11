from pathlib import Path

import pytest

from tests.unit.plugins.framework_specific.workflow_helper import (
    workflow_file_generation_helper,
)


@pytest.mark.kubeflow
@pytest.mark.slow
@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, workflow_name, dependencies, input_parameters",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "kubeflow_workflow_a0_b0",
            {},
            [],
            id="kubeflow_workflow_a0_b0",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "kubeflow_workflow_a0_b0_dependencies",
            {"a0": {"b0"}},
            [],
            id="kubeflow_workflow_a0_b0_dependencies",
        ),
        pytest.param(
            "simple",
            "",
            ["a", "b0"],
            "kubeflow_workflow_a_b0_inputpar",
            {},
            ["b0"],
            id="kubeflow_workflow_a_b0_inputpar",
        ),
        pytest.param(
            "simple_twovar",
            "",
            ["pn"],
            "kubeflow_workflow_two_input_parameter",
            {},
            ["n", "p"],
            id="kubeflow_workflow_two_input_parameter",
        ),
        pytest.param(
            "complex",
            "",
            ["f", "h"],
            "kubeflow_complex_h",
            {},
            [],
            id="kubeflow_complex_h",
        ),
        pytest.param(
            "housing",
            "",
            ["p value"],
            "kubeflow_workflow_housing_simple",
            {},
            [],
            id="kubeflow_workflow_housing_simple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "kubeflow_workflow_housing_multiple",
            {},
            [],
            id="kubeflow_workflow_housing_multiple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "kubeflow_workflow_housing_w_dependencies",
            {"p value": {"y"}},
            [],
            id="kubeflow_workflow_housing_w_dependencies",
        ),
        pytest.param(
            "simple",
            "linear",
            ["a", "linear_second", "linear_third"],
            "kubeflow_hidden_session_dependencies",
            {"linear_third": {"a"}},
            [],
            id="kubeflow_hidden_session_dependencies",
        ),
    ],
)
@pytest.mark.parametrize(
    "dag_config",
    [
        pytest.param(
            {"dag_flavor": "ComponentPerSession"},
            id="kubeflow_workflow_component_per_session",
        ),
        pytest.param(
            {"dag_flavor": "ComponentPerArtifact"},
            id="kubeflow_workflow_component_per_artifact",
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
    Snapshot tests for Kubeflow workflows.
    """

    workflow_file_generation_helper(
        tmp_path,
        linea_db,
        execute,
        input_script1,
        input_script2,
        artifact_list,
        "KUBEFLOW",
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
