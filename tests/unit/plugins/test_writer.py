import pickle
from pathlib import Path

import pytest

from lineapy.api.models.linea_artifact import get_lineaartifactdef
from lineapy.data.types import PipelineType
from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.plugins.pipeline_writer_factory import PipelineWriterFactory
from lineapy.plugins.utils import slugify


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
        pytest.param(
            "simple",
            "linear",
            ["a", "linear_second", "linear_third"],
            "AIRFLOW",
            "airflow_hidden_session_dependencies",
            {"linear_third": {"a"}},
            {"dag_flavor": "PythonOperatorPerArtifact"},
            [],
            id="airflow_hidden_session_dependencies",
        ),
        pytest.param(
            "simple",
            "",
            ["a", "b0"],
            "DVC",
            "dvc_pipeline_a_b0_stageperartifact",
            {},
            {"dag_flavor": "StagePerArtifact"},
            [],
            id="dvc_pipeline_a_b0_stage_per_artifact",
        ),
        pytest.param(
            "simple",
            "",
            ["a"],
            "DVC",
            "dvc_pipeline_a_b0_stageperartifact",
            {},
            {"dag_flavor": "StagePerArtifact"},
            ["b0"],
            id="dvc_pipeline_a_b0_stage_per_artifact_with_input_parameter",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "ARGO",
            "argo_pipeline_a0_b0",
            {},
            {"dag_flavor": "StepPerSession"},
            [],
            id="argo_pipeline_a0_b0_step_per_session",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "KUBEFLOW",
            "kubeflow_pipeline_a0_b0_component_artifact",
            {},
            {"dag_flavor": "ComponentPerArtifact"},
            [],
            id="kubeflow_pipeline_a0_b0_component_artifact",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "KUBEFLOW",
            "kubeflow_pipeline_a0_b0_component_session",
            {},
            {"dag_flavor": "ComponentPerSession"},
            [],
            id="kubeflow_pipeline_a0_b0_component_session",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "RAY",
            "ray_pipeline_a0_b0_task_artifact",
            {},
            {"dag_flavor": "TaskPerArtifact", "use_workflows": False},
            [],
            id="ray_pipeline_a0_b0_task_artifact",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "RAY",
            "ray_pipeline_a0_b0_task_session",
            {},
            {"dag_flavor": "TaskPerSession", "use_workflows": False},
            [],
            id="ray_pipeline_a0_b0_task_session",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "RAY",
            "ray_pipeline_housing_w_dependencies",
            {"p value": {"y"}},
            {},
            [],
            id="ray_pipeline_housing_w_dependencies",
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
    framework,
    pipeline_name,
    dependencies,
    dag_config,
    input_parameters,
    snapshot,
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

    artifact_def_list = [get_lineaartifactdef(art) for art in artifact_list]
    artifact_collection = ArtifactCollection(
        linea_db,
        artifact_def_list,
        input_parameters=input_parameters,
        dependencies=dependencies,
    )

    # Construct pipeline writer
    pipeline_writer = PipelineWriterFactory.get(
        pipeline_type=PipelineType[framework],
        artifact_collection=artifact_collection,
        pipeline_name=pipeline_name,
        output_dir=tmp_path,
        dag_config=dag_config,
    )

    # Write out pipeline files
    pipeline_writer.write_pipeline_files()

    # Get list of files to compare
    file_endings = ["_module.py", "_requirements.txt"]
    if framework in ["AIRFLOW", "ARGO", "KUBEFLOW", "RAY"]:
        file_endings.append("_dag.py")

    file_names = [pipeline_name + file_suffix for file_suffix in file_endings]
    if framework == "DVC":
        file_names.append("dvc.yaml")

        # TODO fix coverage for tests of file per task frameworks to include non artifact tasks
        file_names = file_names + [
            "task_" + art + ".py" for art in artifact_list
        ]

        file_names = file_names + ["params.yaml"]

    # Compare generated vs. expected
    for expected_file_name in file_names:
        path = Path(tmp_path, expected_file_name)
        generated = path.read_text()
        assert generated == snapshot


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
            "complex",
            "",
            ["f", "h"],
            "script_complex_h",
            {},
            id="script_complex_h",
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
    tmp_path,
    linea_db,
    execute,
    input_script1,
    input_script2,
    artifact_list,
    pipeline_name,
    dependencies,
    snapshot,
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

    artifact_def_list = [get_lineaartifactdef(art) for art in artifact_list]
    artifact_collection = ArtifactCollection(
        linea_db,
        artifact_def_list,
        dependencies=dependencies,
    )

    # Construct pipeline writer
    pipeline_writer = PipelineWriterFactory.get(
        pipeline_type=PipelineType.SCRIPT,
        artifact_collection=artifact_collection,
        pipeline_name=pipeline_name,
        output_dir=tmp_path,
        generate_test=True,
    )

    # Write out pipeline files
    pipeline_writer.write_pipeline_files()

    # Compare generated vs. expected
    path_generated = Path(tmp_path, f"test_{pipeline_name}.py")
    content_generated = path_generated.read_text()
    assert content_generated == snapshot

    # Check if artifact values have been (re-)stored
    # to serve as "ground truths" for pipeline testing
    for artname in artifact_list:
        path_generated = Path(
            tmp_path, "sample_output", f"{slugify(artname)}.pkl"
        )
        path_expected = Path(
            "tests",
            "unit",
            "plugins",
            "expected",
            pipeline_name,
            "sample_output",
            f"{slugify(artname)}.pkl",
        )
        with path_generated.open("rb") as fp:
            content_generated = pickle.load(fp)
        with path_expected.open("rb") as fp:
            content_expected = pickle.load(fp)
        assert type(content_generated) == type(content_expected)
