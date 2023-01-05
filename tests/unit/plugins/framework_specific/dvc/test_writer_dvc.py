from pathlib import Path

import pytest

from tests.unit.plugins.framework_specific.pipeline_helper import (
    pipeline_file_generation_helper,
)


@pytest.mark.dvc
@pytest.mark.slow
@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, pipeline_name, dependencies, input_parameters",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "dvc_pipeline_a0_b0",
            {},
            [],
            id="dvc_pipeline_a0_b0",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "dvc_pipeline_a0_b0_dependencies",
            {"a0": {"b0"}},
            [],
            id="dvc_pipeline_a0_b0_dependencies",
        ),
        pytest.param(
            "simple",
            "",
            ["a", "b0"],
            "dvc_pipeline_a_b0_inputpar",
            {},
            ["b0"],
            id="dvc_pipeline_a_b0_inputpar",
        ),
        pytest.param(
            "simple_twovar",
            "",
            ["pn"],
            "dvc_pipeline_two_input_parameter",
            {},
            ["n", "p"],
            id="dvc_pipeline_two_input_parameter",
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
            "dvc_pipeline_housing_simple",
            {},
            [],
            id="dvc_pipeline_housing_simple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "dvc_pipeline_housing_multiple",
            {},
            [],
            id="dvc_pipeline_housing_multiple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "dvc_pipeline_housing_w_dependencies",
            {"p value": {"y"}},
            [],
            id="dvc_pipeline_housing_w_dependencies",
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
            id="dvc_pipeline_stage_per_artifact",
        ),
        pytest.param(
            {"dag_flavor": "SingleStageAllSessions"},
            id="dvc_pipeline_single_stage_all_sessions",
        ),
    ],
)
def test_pipeline_generation(
    tmp_path,
    linea_db,
    execute,
    input_script1,
    input_script2,
    artifact_list,
    pipeline_name,
    dependencies,
    dag_config,
    input_parameters,
    snapshot,
):
    """ """

    pipeline_file_generation_helper(
        tmp_path,
        linea_db,
        execute,
        input_script1,
        input_script2,
        artifact_list,
        "DVC",
        pipeline_name,
        dependencies,
        dag_config,
        input_parameters,
    )

    # Get list of files to compare
    file_endings = ["_module.py", "_requirements.txt", "_dag.py"]

    file_names = [pipeline_name + file_suffix for file_suffix in file_endings]

    # TODO fix coverage for tests of file per task frameworks to include non artifact tasks
    file_names = file_names + ["task_" + art + ".py" for art in artifact_list]

    # Compare generated vs. expected
    for expected_file_name in file_names:
        path = Path(tmp_path, expected_file_name)
        generated = path.read_text()
        assert generated == snapshot
