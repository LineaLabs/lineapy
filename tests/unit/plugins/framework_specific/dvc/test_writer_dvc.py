from pathlib import Path

import pytest

from lineapy.plugins.utils import slugify
from tests.unit.plugins.framework_specific.workflow_helper import (
    workflow_file_generation_helper,
)


@pytest.mark.dvc
@pytest.mark.slow
@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, workflow_name, dependencies, input_parameters",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "dvc_workflow_a0_b0",
            {},
            [],
            id="dvc_workflow_a0_b0",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "dvc_workflow_a0_b0_dependencies",
            {"a0": {"b0"}},
            [],
            id="dvc_workflow_a0_b0_dependencies",
        ),
        pytest.param(
            "simple",
            "",
            ["a", "b0"],
            "dvc_workflow_a_b0_inputpar",
            {},
            ["b0"],
            id="dvc_workflow_a_b0_inputpar",
        ),
        pytest.param(
            "simple_twovar",
            "",
            ["pn"],
            "dvc_workflow_two_input_parameter",
            {},
            ["n", "p"],
            id="dvc_workflow_two_input_parameter",
        ),
        pytest.param(
            "complex",
            "",
            ["f", "h"],
            "dvc_complex_h",
            {},
            [],
            id="dvc_complex_h",
        ),
        pytest.param(
            "housing",
            "",
            ["p value"],
            "dvc_workflow_housing_simple",
            {},
            [],
            id="dvc_workflow_housing_simple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "dvc_workflow_housing_multiple",
            {},
            [],
            id="dvc_workflow_housing_multiple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "dvc_workflow_housing_w_dependencies",
            {"p value": {"y"}},
            [],
            id="dvc_workflow_housing_w_dependencies",
        ),
        pytest.param(
            "simple",
            "linear",
            ["a", "linear_second", "linear_third"],
            "dvc_hidden_session_dependencies",
            {"linear_third": {"a"}},
            [],
            id="dvc_hidden_session_dependencies",
        ),
    ],
)
@pytest.mark.parametrize(
    "dag_config",
    [
        pytest.param(
            {"dag_flavor": "StagePerArtifact"},
            id="dvc_workflow_stage_per_artifact",
        ),
        pytest.param(
            {"dag_flavor": "SingleStageAllSessions"},
            id="dvc_workflow_single_stage_all_sessions",
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
    Snapshot tests for DVC workflows.
    """

    workflow_file_generation_helper(
        tmp_path,
        linea_db,
        execute,
        input_script1,
        input_script2,
        artifact_list,
        "DVC",
        workflow_name,
        dependencies,
        dag_config,
        input_parameters,
    )

    # Get list of files to compare
    file_endings = ["_module.py", "_requirements.txt"]
    file_names = [workflow_name + file_suffix for file_suffix in file_endings]
    file_names.append("dvc.yaml")

    # TODO fix coverage for tests of file per task frameworks to include non artifact tasks
    if dag_config["dag_flavor"] != "SingleStageAllSessions":
        file_names = file_names + [
            "task_" + slugify(art) + ".py" for art in artifact_list
        ]

    # Compare generated vs. expected
    for expected_file_name in file_names:
        path = Path(tmp_path, expected_file_name)
        generated = path.read_text()
        assert generated == snapshot
