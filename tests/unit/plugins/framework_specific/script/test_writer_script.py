from pathlib import Path

import pytest

from tests.unit.plugins.framework_specific.workflow_helper import (
    workflow_file_generation_helper,
)


@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, workflow_name, dependencies, dag_config, input_parameters",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "script_workflow_a0_b0",
            {},
            {},
            [],
            id="script_workflow_a0_b0",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "script_workflow_a0_b0_dependencies",
            {"a0": {"b0"}},
            {},
            [],
            id="script_workflow_a0_b0_dependencies",
        ),
        pytest.param(
            "simple",
            "",
            ["a", "b0"],
            "script_workflow_a_b0_inputpar",
            {},
            {},
            ["b0"],
            id="script_workflow_a_b0_inputpar",
        ),
        pytest.param(
            "simple_twovar",
            "",
            ["pn"],
            "script_workflow_two_input_parameter",
            {},
            {},
            ["n", "p"],
            id="script_workflow_two_input_parameter",
        ),
        pytest.param(
            "complex",
            "",
            ["f", "h"],
            "script_complex_h",
            {},
            {"dag_flavor": "PythonOperatorPerArtifact"},
            [],
            id="script_complex_h",
        ),
        pytest.param(
            "housing",
            "",
            ["p value"],
            "script_workflow_housing_simple",
            {},
            {},
            [],
            id="script_workflow_housing_simple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "script_workflow_housing_multiple",
            {},
            {},
            [],
            id="script_workflow_housing_multiple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "script_workflow_housing_w_dependencies",
            {"p value": {"y"}},
            {},
            [],
            id="script_workflow_housing_w_dependencies",
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
    Snapshot tests for Script type workflows.
    """

    workflow_file_generation_helper(
        tmp_path,
        linea_db,
        execute,
        input_script1,
        input_script2,
        artifact_list,
        "SCRIPT",
        workflow_name,
        dependencies,
        dag_config,
        input_parameters,
    )

    # Get list of files to compare
    file_endings = ["_module.py", "_requirements.txt"]

    file_names = [workflow_name + file_suffix for file_suffix in file_endings]

    # Compare generated vs. expected
    for expected_file_name in file_names:
        path = Path(tmp_path, expected_file_name)
        generated = path.read_text()
        assert generated == snapshot
