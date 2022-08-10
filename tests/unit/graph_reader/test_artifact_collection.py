import pathlib
import shutil
import tempfile

import pytest

from lineapy.utils.utils import prettify


@pytest.mark.parametrize(
    "input_script, artifact_list, expected_output",
    [
        pytest.param(
            "extract_common",
            ["b", "c"],
            "ac_extract_common_all",
            id="extract_common_all",
        ),
        pytest.param(
            "extract_common",
            ["b"],
            "ac_extract_common_partial",
            id="extract_common_partial",
        ),
        pytest.param(
            "mutate_after_save",
            ["a", "b"],
            "ac_mutate_after_save_all",
            id="mutate_after_save_all",
        ),
        pytest.param(
            "module_import",
            ["df", "df2"],
            "ac_module_import_all",
            id="module_import_all",
        ),
        pytest.param(
            "module_import_alias",
            ["df", "df2"],
            "ac_module_import_alias_all",
            id="module_import_alias_all",
        ),
        pytest.param(
            "module_import_from",
            ["iris_model", "iris_petal_length_pred"],
            "ac_module_import_from_all",
            id="module_import_from_all",
        ),
        pytest.param(
            "complex",
            ["a", "a0", "c", "f", "e", "g2", "h", "z"],
            "ac_complex_graph_all",
            id="complex_graph_all",
        ),
        pytest.param(
            "complex",
            ["a0", "c", "h"],
            "ac_complex_graph_a0_c_h",
            id="complex_graph_a0_c_h",
        ),
        pytest.param(
            "complex",
            ["h"],
            "ac_complex_graph_h",
            id="ac_complex_graph_h",
        ),
    ],
)
def test_one_session(execute, input_script, artifact_list, expected_output):
    """
    Test code refactor
    """

    code = pathlib.Path(
        "tests/unit/graph_reader/inputs/" + input_script
    ).read_text()
    res = execute(code, snapshot=False)

    artifact_string = ", ".join([f'"{x}"' for x in artifact_list])
    code = (
        "from lineapy.graph_reader.artifact_collection import ArtifactCollection\n"
        + f"ac = ArtifactCollection([{artifact_string}])"
    )
    res = execute(code, snapshot=False)
    ac = res.values["ac"]
    refactor_result = ac.generate_module()
    expected_result = pathlib.Path(
        "tests/unit/graph_reader/expected/" + expected_output
    ).read_text()
    assert prettify(refactor_result) == prettify(expected_result)


@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, expected_output, dependencies",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "two_session_a0_b0",
            {},
            id="two_session_a0_b0",
        ),
        pytest.param(
            "simple",
            "complex",
            ["b0", "a0"],
            "two_session_b0_a0_dependencies",
            {"b0": {"a0"}},
            id="two_session_b0_a0_dependencies",
        ),
        pytest.param(
            "simple",
            "complex",
            ["b0", "a0"],
            "two_session_b0_a0_dependencies2",
            {"a0": {"b0"}},
            id="two_session_b0_a0_dependencies2",
        ),
        pytest.param(
            "module_import_alias",
            "module_import_from",
            ["df", "iris_model", "iris_petal_length_pred"],
            "two_session_df_iris",
            {},
            id="two_session_df_iris",
        ),
    ],
)
def test_two_session(
    execute,
    input_script1,
    input_script2,
    artifact_list,
    expected_output,
    dependencies,
):
    """
    Test two sessions
    """

    code1 = pathlib.Path(
        "tests/unit/graph_reader/inputs/" + input_script1
    ).read_text()
    res = execute(code1, snapshot=False)

    code2 = pathlib.Path(
        "tests/unit/graph_reader/inputs/" + input_script2
    ).read_text()
    res = execute(code2, snapshot=False)

    artifact_string = ", ".join([f'"{x}"' for x in artifact_list])
    code = (
        "from lineapy.graph_reader.artifact_collection import ArtifactCollection\n"
        + f"ac = ArtifactCollection([{artifact_string}])"
    )
    res = execute(code, snapshot=False)
    ac = res.values["ac"]
    refactor_result = ac.generate_module(dependencies)
    expected_result = pathlib.Path(
        "tests/unit/graph_reader/expected/" + expected_output
    ).read_text()
    assert prettify(refactor_result) == prettify(expected_result)


def check_requirements_txt(t1: str, t2: str):
    return set(t1.split("\n")) == set(t2.split("\n"))


@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, framework, pipeline_name, dependencies, airflow_dag_config",
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
    airflow_dag_config,
):
    """
    Test two sessions
    """

    code1 = pathlib.Path(
        "tests/unit/graph_reader/inputs/" + input_script1
    ).read_text()
    res = execute(code1, snapshot=False)

    if input_script2 != "":
        code2 = pathlib.Path(
            "tests/unit/graph_reader/inputs/" + input_script2
        ).read_text()
        res = execute(code2, snapshot=False)

    artifact_string = ", ".join([f'"{x}"' for x in artifact_list])
    code = (
        "from lineapy.graph_reader.artifact_collection import ArtifactCollection\n"
        + f"ac = ArtifactCollection([{artifact_string}])"
    )
    res = execute(code, snapshot=False)
    ac = res.values["ac"]
    tempfolder = tempfile.mkdtemp()
    ac.generate_pipeline_files(
        framework=framework,
        dependencies=dependencies,
        pipeline_name=pipeline_name,
        output_dir=tempfolder,
        airflow_dag_config=airflow_dag_config,
        airflow_dag_flavor="PythonOperatorPerSession",
    )

    file_endings = ["_module.py", "_requirements.txt", "_Dockerfile"]
    if framework != "SCRIPT":
        file_endings.append("_dag.py")

    for file_suffix in file_endings:
        path = pathlib.Path(
            f"{tempfolder}/{pipeline_name}/{pipeline_name}{file_suffix}"
        )
        generated = path.read_text()
        path_expected = pathlib.Path(
            f"tests/unit/graph_reader/expected/{pipeline_name}/{pipeline_name}{file_suffix}"
        )
        if file_suffix != "_requirements.txt":
            to_compare = path_expected.read_text()
            if file_suffix.endswith(".py"):
                to_compare = prettify(to_compare)
                generated = prettify(generated)
            assert generated == to_compare
        else:
            assert check_requirements_txt(
                path.read_text(), path_expected.read_text()
            )

    shutil.rmtree(tempfolder)
