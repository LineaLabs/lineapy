import tempfile
from pathlib import Path

import pytest

from lineapy.graph_reader.artifact_collection import ArtifactCollection
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
    "input_script1, input_script2, artifact_list, framework, pipeline_name, dependencies, dag_config, input_parameters",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "SCRIPT",
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
            "AIRFLOW",
            "airflow_pipeline_a0_b0",
            {},
            {},
            [],
            id="airflow_pipeline_a0_b0",
        ),
        pytest.param(
            "simple",
            "",
            ["a", "b0"],
            "AIRFLOW",
            "airflow_pipeline_a_b0_inputpar",
            {},
            {"dag_flavor": "PythonOperatorPerArtifact"},
            ["b0"],
            id="airflow_pipeline_a_b0_input_parameter_per_artifact",
        ),
        pytest.param(
            "simple",
            "",
            ["a", "b0"],
            "AIRFLOW",
            "airflow_pipeline_a_b0_inputpar_session",
            {},
            {"dag_flavor": "PythonOperatorPerSession"},
            ["b0"],
            id="airflow_pipeline_a_b0_input_parameter_per_session",
        ),
        pytest.param(
            "simple_twovar",
            "",
            ["pn"],
            "AIRFLOW",
            "airflow_pipeline_two_input_parameter",
            {},
            {"dag_flavor": "PythonOperatorPerArtifact"},
            ["n", "p"],
            id="airflow_pipeline_two_input_parameter",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "SCRIPT",
            "script_pipeline_a0_b0_dependencies",
            {"a0": {"b0"}},
            {},
            [],
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
            [],
            id="airflow_pipeline_a0_b0_dependencies",
        ),
        pytest.param(
            "housing",
            "",
            ["p value"],
            "SCRIPT",
            "script_pipeline_housing_simple",
            {},
            {},
            [],
            id="script_pipeline_housing_simple",
        ),
        pytest.param(
            "housing",
            "",
            ["p value"],
            "AIRFLOW",
            "airflow_pipeline_housing_simple",
            {},
            {},
            [],
            id="airflow_pipeline_housing_simple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "SCRIPT",
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
            "AIRFLOW",
            "airflow_pipeline_housing_multiple",
            {},
            {},
            [],
            id="airflow_pipeline_housing_multiple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "SCRIPT",
            "script_pipeline_housing_w_dependencies",
            {"p value": {"y"}},
            {},
            [],
            id="script_pipeline_housing_w_dependencies",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "AIRFLOW",
            "airflow_pipeline_housing_w_dependencies",
            {"p value": {"y"}},
            {},
            [],
            id="airflow_pipeline_housing_w_dependencies",
        ),
        pytest.param(
            "complex",
            "",
            ["f", "h"],
            "AIRFLOW",
            "airflow_complex_h_perart",
            {},
            {"dag_flavor": "PythonOperatorPerArtifact"},
            [],
            id="airflow_complex_h_perartifact",
        ),
    ],
)
def test_pipeline_generation(
    linea_db,
    execute,
    input_script1,
    input_script2,
    artifact_list,
    framework,
    pipeline_name,
    dependencies,
    dag_config,
    input_parameters,
):
    """
    Test two sessions
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

    artifact_collection = ArtifactCollection(
        linea_db, artifact_list, input_parameters=input_parameters
    )
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
            path = Path(tempfolder, pipeline_name + file_suffix)
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


@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, pipeline_name, dependencies",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "script_pipeline_a0_b0_dependencies",
            {"a0": {"b0"}},
            id="script_pipeline_a0_b0_dependencies",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "script_pipeline_housing_w_dependencies",
            {"p value": {"y"}},
            id="script_pipeline_housing_w_dependencies",
        ),
    ],
)
def test_pipeline_test_generation(
    linea_db,
    execute,
    input_script1,
    input_script2,
    artifact_list,
    pipeline_name,
    dependencies,
):
    code1 = Path(
        "tests", "unit", "graph_reader", "inputs", input_script1
    ).read_text()
    execute(code1, snapshot=False)

    if input_script2 != "":
        code2 = Path(
            "tests", "unit", "graph_reader", "inputs", input_script2
        ).read_text()
        execute(code2, snapshot=False)

    artifact_collection = ArtifactCollection(linea_db, artifact_list)
    with tempfile.TemporaryDirectory() as tempfolder:
        pipeline_writer = pipeline_writer_classes["SCRIPT"](
            artifact_collection,
            dependencies=dependencies,
            pipeline_name=pipeline_name,
            output_dir=tempfolder,
        )
        pipeline_writer.write_pipeline_files()

        # Compare generated vs. expected
        path_generated = Path(tempfolder, f"test_{pipeline_name}.py")
        content_generated = path_generated.read_text()
        path_expected = Path(
            "tests",
            "unit",
            "plugins",
            "expected",
            pipeline_name,
            f"test_{pipeline_name}.py",
        )
        content_expected = prettify(path_expected.read_text())
        assert content_generated == content_expected
