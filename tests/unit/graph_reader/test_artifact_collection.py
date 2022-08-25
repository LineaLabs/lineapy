import pathlib

import pytest


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
def test_one_session(execute, input_script, artifact_list):
    """
    Test code refactor, make sure each artifact has a dedicated function in the
    generated module.
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
    module = ac.get_module()
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
def test_two_session(
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
    module = ac.get_module()
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
        moduletext = ac.generate_module_text(dependencies)
        first_artifact_in_session = {}
        for sa in ac.session_artifacts.values():
            for nodecollection in sa.artifact_nodecollections:
                first_artifact_in_session[nodecollection.name] = (
                    "run_session_including_" + sa._get_first_artifact_name()
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
