from pathlib import Path

import pytest

from tests.unit.plugins.framework_specific.pipeline_helper import (
    pipeline_file_generation_helper,
)


@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, pipeline_name, dependencies, dag_config, input_parameters",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "script_pipeline_a0_b0",
            {},
            {},
            [],
            id="script_pipeline_a0_b0",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "script_pipeline_a0_b0_dependencies",
            {"a0": {"b0"}},
            {},
            [],
            id="script_pipeline_a0_b0_dependencies",
        ),
        pytest.param(
            "simple",
            "",
            ["a", "b0"],
            "script_pipeline_a_b0_inputpar",
            {},
            {},
            ["b0"],
            id="script_pipeline_a_b0_inputpar",
        ),
        pytest.param(
            "simple_twovar",
            "",
            ["pn"],
            "script_pipeline_two_input_parameter",
            {},
            {},
            ["n", "p"],
            id="script_pipeline_two_input_parameter",
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
            "script_pipeline_housing_simple",
            {},
            {},
            [],
            id="script_pipeline_housing_simple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "script_pipeline_housing_multiple",
            {},
            {},
            [],
            id="script_pipeline_housing_multiple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "script_pipeline_housing_w_dependencies",
            {"p value": {"y"}},
            {},
            [],
            id="script_pipeline_housing_w_dependencies",
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
    """
    Test two sessions
    """

    pipeline_file_generation_helper(
        tmp_path,
        linea_db,
        execute,
        input_script1,
        input_script2,
        artifact_list,
        "SCRIPT",
        pipeline_name,
        dependencies,
        dag_config,
        input_parameters,
    )

    # Get list of files to compare
    file_endings = ["_module.py", "_requirements.txt"]
    # if framework in ["AIRFLOW", "ARGO", "KUBEFLOW", "RAY"]:
    #     file_endings.append("_dag.py")

    file_names = [pipeline_name + file_suffix for file_suffix in file_endings]
    # if framework == "DVC":
    #     file_names.append("dvc.yaml")

    #     # TODO fix coverage for tests of file per task frameworks to include non artifact tasks
    #     file_names = file_names + [
    #         "task_" + art + ".py" for art in artifact_list
    #     ]

    # Compare generated vs. expected
    for expected_file_name in file_names:
        path = Path(tmp_path, expected_file_name)
        generated = path.read_text()
        assert generated == snapshot
