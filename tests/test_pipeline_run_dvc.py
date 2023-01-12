import subprocess
from pathlib import Path

import pytest

from lineapy.api.models.linea_artifact import get_lineaartifactdef
from lineapy.data.types import PipelineType
from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.plugins.pipeline_writer_factory import PipelineWriterFactory


@pytest.mark.skipif(
    subprocess.check_call(["git", "--version"]) != 0,
    reason="dvc requires git to be installed",
)
@pytest.mark.dvc
@pytest.mark.slow
@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, pipeline_name, dependencies, dag_config, input_parameters",
    [
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "dvc_pipeline_housing_artifacts_w_dependencies",
            {"p value": {"y"}},
            {"dag_flavor": "StagePerArtifact"},
            [],
            id="dvc_pipeline_housing_artifacts_w_dependencies",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "dvc_pipeline_housing_session_w_dependencies",
            {"p value": {"y"}},
            {
                # TODO LIN-626 add dag config for per session flavor
            },
            [],
            id="dvc_pipeline_housing_session_w_dependencies",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "script_pipeline_a0_b0_dependencies",
            {"a0": {"b0"}},
            {},
            [],
            id="dvc_two_session_w_dependencies",
        ),
    ],
)
def test_run_dvc_dag(
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
    Verifies that the dvc flavored pipeline APIs produce a working dvc DAG
    by running the DAG locally.
    """

    code1 = Path(
        "tests", "unit", "graph_reader", "inputs", input_script1
    ).read_text()
    execute(code1, snapshot=False)

    if input_script2 != "":
        code2 = Path(
            "tests", "unit", "graph_reader", "inputs", input_script2
        ).read_text()
        execute(code2, snapshot=False)

    # Write out pipeline files
    artifact_def_list = [get_lineaartifactdef(art) for art in artifact_list]
    artifact_collection = ArtifactCollection(
        linea_db,
        artifact_def_list,
        input_parameters=input_parameters,
        dependencies=dependencies,
    )

    # Construct pipeline writer
    pipeline_writer = PipelineWriterFactory.get(
        pipeline_type=PipelineType.DVC,
        artifact_collection=artifact_collection,
        pipeline_name=pipeline_name,
        output_dir=tmp_path,
        dag_config=dag_config,
    )
    pipeline_writer.write_pipeline_files()

    # Run dvc in new virtual env so we don't end up with version conflicts
    # with lineapy deps
    # https://github.com/man-group/pytest-plugins/tree/master/pytest-virtualenv#installing-packages

    req_path = Path(tmp_path, f"{pipeline_name}_requirements.txt")
    virtualenv.run(f"pip install -r {req_path}", capture=False, cd=".")
    virtualenv.run(
        "pip install -r test_pipeline_dvc_req.txt", capture=False, cd="."
    )

    virtualenv.run("git init", capture=False, cd=tmp_path)
    virtualenv.run("dvc init", capture=False, cd=tmp_path)

    # This run command will error if the dag is not runnable by dvc
    out = virtualenv.run("dvc repro", capture=True, cd=tmp_path)
    print(out)
