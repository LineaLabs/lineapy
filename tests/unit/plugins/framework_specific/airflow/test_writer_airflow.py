from pathlib import Path

import pytest

from tests.unit.plugins.framework_specific.pipeline_helper import (
    pipeline_file_generation_helper,
)


@pytest.mark.airflow
@pytest.mark.slow
@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, pipeline_name, dependencies, input_parameters",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "airflow_pipeline_a0_b0",
            {},
            [],
            id="airflow_pipeline_a0_b0",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "airflow_pipeline_a0_b0_dependencies",
            {"a0": {"b0"}},
            [],
            id="airflow_pipeline_a0_b0_dependencies",
        ),
        pytest.param(
            "simple",
            "",
            ["a", "b0"],
            "airflow_pipeline_a_b0_inputpar",
            {},
            ["b0"],
            id="airflow_pipeline_a_b0_inputpar",
        ),
        pytest.param(
            "simple_twovar",
            "",
            ["pn"],
            "airflow_pipeline_two_input_parameter",
            {},
            ["n", "p"],
            id="airflow_pipeline_two_input_parameter",
        ),
        pytest.param(
            "complex",
            "",
            ["f", "h"],
            "airflow_complex_h",
            {},
            [],
            id="airflow_complex_h",
        ),
        pytest.param(
            "housing",
            "",
            ["p value"],
            "airflow_pipeline_housing_simple",
            {},
            [],
            id="airflow_pipeline_housing_simple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "airflow_pipeline_housing_multiple",
            {},
            [],
            id="airflow_pipeline_housing_multiple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "airflow_pipeline_housing_w_dependencies",
            {"p value": {"y"}},
            [],
            id="airflow_pipeline_housing_w_dependencies",
        ),
        pytest.param(
            "simple",
            "linear",
            ["a", "linear_second", "linear_third"],
            "airflow_hidden_session_dependencies",
            {"linear_third": {"a"}},
            [],
            id="airflow_hidden_session_dependencies",
        ),
    ],
)
@pytest.mark.parametrize(
    "dag_config",
    [
        pytest.param(
            {"dag_flavor": "PythonOperatorPerSession"},
            id="airflow_pipeline_operator_per_session",
        ),
        pytest.param(
            {"dag_flavor": "PythonOperatorPerArtifact"},
            id="airflow_pipeline_operator_per_artifact",
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
        "AIRFLOW",
        pipeline_name,
        dependencies,
        dag_config,
        input_parameters,
    )

    # Get list of files to compare
    file_endings = ["_module.py", "_requirements.txt", "_dag.py"]

    file_names = [pipeline_name + file_suffix for file_suffix in file_endings]

    # Compare generated vs. expected
    for expected_file_name in file_names:
        path = Path(tmp_path, expected_file_name)
        generated = path.read_text()
        assert generated == snapshot
