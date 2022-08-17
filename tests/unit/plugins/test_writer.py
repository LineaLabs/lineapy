import tempfile
from pathlib import Path

import pytest

from lineapy.plugins.pipeline_writers import (
    AirflowPipelineWriter,
    BasePipelineWriter,
)
from lineapy.utils.utils import get_system_python_version, prettify

pipeline_writer_classes = {
    "SCRIPT": BasePipelineWriter,
    "AIRFLOW": AirflowPipelineWriter,
}


def check_requirements_txt(t1: str, t2: str):
    return set(t1.split("\n")) == set(t2.split("\n"))


@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, framework, pipeline_name, dependencies, dag_config",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "SCRIPT",
            "script_pipeline_a0_b0",
            {},
            {},
            id="script_pipeline_a0_b0",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "AIRFLOW",
            "airflow_pipeline_a0_b0",
            {},
            {},
            id="airflow_pipeline_a0_b0",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "SCRIPT",
            "script_pipeline_a0_b0_dependencies",
            {"a0": {"b0"}},
            {},
            id="script_pipeline_a0_b0_dependencies",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "AIRFLOW",
            "airflow_pipeline_a0_b0_dependencies",
            {"a0": {"b0"}},
            {},
            id="airflow_pipeline_a0_b0_dependencies",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "SCRIPT",
            "script_pipeline_housing_w_dependencies",
            {"p value": {"y"}},
            {},
            id="script_pipeline_housing_w_dependencies",
        ),
    ],
)
def test_pipeline_generation(
    execute,
    input_script1,
    input_script2,
    artifact_list,
    framework,
    pipeline_name,
    dependencies,
    dag_config,
):
    """
    Test two sessions
    """

    code1 = Path(
        "tests", "unit", "graph_reader", "inputs", input_script1
    ).read_text()
    res = execute(code1, snapshot=False)

    if input_script2 != "":
        code2 = Path(
            "tests", "unit", "graph_reader", "inputs", input_script2
        ).read_text()
        res = execute(code2, snapshot=False)

    artifact_string = ", ".join([f'"{x}"' for x in artifact_list])
    code = (
        "from lineapy.graph_reader.artifact_collection import ArtifactCollection\n"
        + f"ac = ArtifactCollection([{artifact_string}])"
    )
    res = execute(code, snapshot=False)
    artifact_collection = res.values["ac"]

    with tempfile.TemporaryDirectory() as tempfolder:
        pipeline_writer = pipeline_writer_classes[framework](
            artifact_collection,
            dependencies=dependencies,
            pipeline_name=pipeline_name,
            output_dir=tempfolder,
            dag_config=dag_config,
        )
        pipeline_writer.write_pipeline_files()

        file_endings = ["_module.py", "_requirements.txt", "_Dockerfile"]
        if framework != "SCRIPT":
            file_endings.append("_dag.py")

        for file_suffix in file_endings:
            path = Path(tempfolder, pipeline_name, pipeline_name + file_suffix)
            generated = path.read_text()
            path_expected = Path(
                "tests",
                "unit",
                "plugins",
                "expected",
                pipeline_name,
                pipeline_name + file_suffix,
            )
            if file_suffix == "_requirements.txt":
                assert check_requirements_txt(
                    generated, path_expected.read_text()
                )
            else:
                to_compare = path_expected.read_text()
                if file_suffix == "_Dockerfile":
                    to_compare = to_compare.format(
                        python_version=get_system_python_version()
                    )
                if file_suffix.endswith(".py"):
                    to_compare = prettify(to_compare)
                assert generated == to_compare
