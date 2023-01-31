import os
import subprocess

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
@pytest.mark.slow
def test_run_script_dag(
    virtualenv,
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
):
    """
    Verifies that the DAGs we produce do run successfully.
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

    os.chdir(str(tmp_path))

    subprocess.check_call(["python", f"{pipeline_name}_module.py"])
