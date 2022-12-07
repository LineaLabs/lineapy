import pathlib
import subprocess

import pytest

from lineapy.api.models.linea_artifact import get_lineaartifactdef
from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.plugins.base_pipeline_writer import BasePipelineWriter
from lineapy.plugins.loader import load_as_module


@pytest.mark.parametrize(
    "input_script, artifact_list",
    [
        pytest.param(
            "extract_common",
            ["b", "c"],
            id="extract_common_all",
        ),
        pytest.param(
            "extract_common",
            ["b"],
            id="extract_common_partial",
        ),
        pytest.param(
            "mutate_after_save",
            ["a", "b"],
            id="mutate_after_save_all",
        ),
        pytest.param(
            "module_import",
            ["df", "df2"],
            id="module_import_all",
        ),
        pytest.param(
            "module_import_alias",
            ["df", "df2"],
            id="module_import_alias_all",
        ),
        pytest.param(
            "module_import_from",
            ["iris_model", "iris_petal_length_pred"],
            id="module_import_from_all",
        ),
        pytest.param(
            "complex",
            ["a", "a0", "c", "f", "e", "g2", "h", "z"],
            id="complex_graph_all",
        ),
        pytest.param(
            "complex",
            ["a0", "c", "h"],
            id="complex_graph_a0_c_h",
        ),
        pytest.param(
            "complex",
            ["h"],
            id="ac_complex_graph_h",
        ),
    ],
)
def test_one_session(linea_db, execute, input_script, artifact_list):
    """
    Test code refactor, make sure each artifact has a dedicated function in the
    generated module.
    """

    artifact_string = ", ".join([f'"{x}"' for x in artifact_list])
    code = pathlib.Path(
        "tests/unit/graph_reader/inputs/" + input_script
    ).read_text()

    execute(code, snapshot=False)
    artifact_def_list = [get_lineaartifactdef(art) for art in artifact_list]
    ac = ArtifactCollection(linea_db, artifact_def_list)
    writer = BasePipelineWriter(ac)
    module = load_as_module(writer)
    # Check there is a get_{artifact} function in the module for all artifacts
    assert all(
        [
            f"get_{art.replace(' ','_')}" in module.__dir__()
            for art in artifact_list
        ]
    )


@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, dependencies",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            {},
            id="two_session_a0_b0",
        ),
        pytest.param(
            "simple",
            "complex",
            ["b0", "a0"],
            {"b0": {"a0"}},
            id="two_session_b0_a0_dependencies",
        ),
        pytest.param(
            "simple",
            "complex",
            ["b0", "a0"],
            {"a0": {"b0"}},
            id="two_session_b0_a0_dependencies2",
        ),
        pytest.param(
            "module_import_alias",
            "module_import_from",
            ["df", "iris_model", "iris_petal_length_pred"],
            {},
            id="two_session_df_iris",
        ),
    ],
)
def test_two_sessions(
    linea_db,
    execute,
    input_script1,
    input_script2,
    artifact_list,
    dependencies,
):
    """
    Test code refactor with two artifacts, make sure each artifact has a
    dedicated function in the generated module. If any dependencies is
    specified, make sure the session is run in proper order in the
    run_all_sessions block.
    """

    session1_code = pathlib.Path(
        "tests/unit/graph_reader/inputs/" + input_script1
    ).read_text()
    execute(session1_code, snapshot=False)

    session2_code = pathlib.Path(
        "tests/unit/graph_reader/inputs/" + input_script2
    ).read_text()

    code = session2_code
    execute(code, snapshot=False)
    artifact_def_list = [get_lineaartifactdef(art) for art in artifact_list]
    ac = ArtifactCollection(linea_db, artifact_def_list)
    writer = BasePipelineWriter(ac)
    module = load_as_module(writer)
    # Check there is a get_{artifact} function in the module for all artifacts
    assert all(
        [
            f"get_{art.replace(' ','_')}" in module.__dir__()
            for art in artifact_list
        ]
    )

    # If dependencies have been set, check whether the run_session_including_{art}
    # show up in correct order
    if len(dependencies) > 0:
        ac = ArtifactCollection(
            linea_db, artifact_def_list, dependencies=dependencies
        )
        writer = BasePipelineWriter(ac)
        moduletext = writer._compose_module()
        first_artifact_in_session = {}
        for sa in ac.session_artifacts.values():
            for nodecollection in sa.usercode_nodecollections:
                art_name = sa._get_first_artifact_name()
                assert isinstance(art_name, str)
                first_artifact_in_session[nodecollection.name] = (
                    "run_session_including_" + art_name
                )

        for art, art_predecessors in dependencies.items():
            art_session_line = first_artifact_in_session[art]
            art_session_line_index = moduletext.find(art_session_line)
            # run_session for art exists
            assert art_session_line_index >= 0
            for art_pred in art_predecessors:
                art_pred_session_line = first_artifact_in_session[art_pred]
                art_pred_session_line_index = moduletext.find(
                    art_pred_session_line
                )
                # run_session for required art exists
                assert art_pred_session_line_index >= 0
                # required art session is in from of art session
                assert art_pred_session_line_index < art_session_line_index
        print(moduletext)


def test_dependencies(linea_db, execute):
    """
    Check sort_session_artifacts withing artifactcollection
    """
    code = """\n
import lineapy
a = 1
b = 2
c = a+b
lineapy.save(a,'a')
lineapy.save(b,'b')
lineapy.save(c,'c')
"""
    execute(code, snapshot=False)
    ac = ArtifactCollection(
        linea_db,
        target_artifacts=[
            get_lineaartifactdef("b"),
            get_lineaartifactdef("c"),
        ],
        reuse_pre_computed_artifacts=[get_lineaartifactdef("b")],
        input_parameters=["a"],
        dependencies={"c": {"b"}},
    )
    writer = BasePipelineWriter(ac)
    module = load_as_module(writer)
    assert not hasattr(module, "get_a")
    assert hasattr(module, "get_b")
    assert hasattr(module, "get_c")


@pytest.mark.parametrize(
    "input_parameters, input_values, expected_values",
    [
        pytest.param([], dict(), {"prod_p": "pp"}, id="no_input"),
        pytest.param(["a", "p"], dict(), {"prod_p": "pp"}, id="default_value"),
        pytest.param(
            ["a", "p"],
            {"a": 5, "p": "P"},
            {"prod_p": "PPPPP"},
            id="overriding_value",
        ),
    ],
)
def test_module_run(
    tmpdir,
    linea_db,
    execute,
    input_parameters,
    input_values,
    expected_values,
):
    """
    Test the module generated from ArtifactCollection can run with/without
    input parameters
    """

    code = """\n
import lineapy
a = 2
p = "p"
b = p*a
lineapy.save(b,'prod_p')
"""
    execute(code, snapshot=False)
    artifact_list = ["prod_p"]
    artifact_defs_list = [get_lineaartifactdef(art) for art in artifact_list]
    ac = ArtifactCollection(
        linea_db,
        artifact_defs_list,
        input_parameters=input_parameters,
        dependencies={},
    )
    writer = BasePipelineWriter(ac)
    temp_module_path = pathlib.Path(tmpdir, "artifactcollection_module.py")
    with open(temp_module_path, "w") as f:
        f.writelines(writer._compose_module())

    cmds = ["python", str(temp_module_path)]
    # Add input parameter values if specified in cmds
    for par, val in input_values.items():
        cmds += [f"--{par}", str(val)]

    p = subprocess.run(cmds, capture_output=True, text=True)
    assert p.returncode == 0
    module_run_result = eval(p.stdout)
    assert all([art in module_run_result.keys() for art in artifact_list])
    assert all([module_run_result[k] == v for k, v in expected_values.items()])
