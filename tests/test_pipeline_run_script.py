import os
import subprocess
from pathlib import Path

import pytest

from lineapy.api.models.linea_artifact import get_lineaartifactdef
from lineapy.data.types import PipelineType
from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.plugins.pipeline_writer_factory import PipelineWriterFactory


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
        pipeline_type=PipelineType.SCRIPT,
        artifact_collection=artifact_collection,
        pipeline_name=pipeline_name,
        output_dir=tmp_path,
        dag_config=dag_config,
    )
    pipeline_writer.write_pipeline_files()

    os.chdir(str(tmp_path))

    subprocess.check_call(["python", f"{pipeline_name}_module.py"])
