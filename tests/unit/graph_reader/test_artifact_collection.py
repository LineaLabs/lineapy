import pathlib

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
def test_refactor(execute, input_script, artifact_list, expected_output):
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
    # art = res.values["art"]
    # sas = SessionArtifacts([art[art_name] for art_name in artifact_list])
    # ac = ArtifactCollection(artifact_list)
    ac = res.values["ac"]
    refactor_result = ac.generate_module()
    expected_result = pathlib.Path(
        "tests/unit/graph_reader/expected/" + expected_output
    ).read_text()
    assert prettify(refactor_result) == prettify(expected_result)
