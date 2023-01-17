from pathlib import Path

import pytest

from tests.unit.plugins.framework_specific.pipeline_helper import (
    pipeline_file_generation_helper,
)


@pytest.mark.ray
@pytest.mark.slow
@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, pipeline_name, dependencies, dag_config, input_parameters",
    [
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "ray_pipeline_housing_artifacts_w_dependencies",
            {"p value": {"y"}},
            {
                "dag_flavor": "TaskPerArtifact",
            },
            [],
            id="ray_pipeline_housing_artifacts_w_dependencies",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "ray_pipeline_housing_session_w_dependencies",
            {"p value": {"y"}},
            # two return values on this task so must use old remote API
            {"dag_flavor": "TaskPerSession", "use_workflows": False},
            [],
            id="ray_pipeline_housing_session_w_dependencies",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "script_pipeline_a0_b0_dependencies",
            {"a0": {"b0"}},
            {"dag_flavor": "TaskPerSession"},
            [],
            id="ray_two_session_w_dependencies",
        ),
    ],
)
def test_run_ray_dag(
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
    Verifies that the ray flavored pipeline APIs produce a working ray DAG
    by running the DAG locally.
    """

    pipeline_file_generation_helper(
        tmp_path,
        linea_db,
        execute,
        input_script1,
        input_script2,
        artifact_list,
        "RAY",
        pipeline_name,
        dependencies,
        dag_config,
        input_parameters,
    )

    # Run ray in new virtual env so we don't end up with version conflicts
    # with lineapy deps
    # https://github.com/man-group/pytest-plugins/tree/master/pytest-virtualenv#installing-packages
    req_path = Path(tmp_path, f"{pipeline_name}_requirements.txt")
    virtualenv.run(f"pip install -r {req_path}", capture=False, cd=".")
    virtualenv.run(
        "pip install -r test_pipeline_ray_req.txt", capture=False, cd="."
    )

    dag_path = Path(tmp_path, f"{pipeline_name}_dag.py")

    # This run command will error if the dag is not runnable by ray
    virtualenv.run(
        f"python {dag_path}",
        capture=True,
    )
