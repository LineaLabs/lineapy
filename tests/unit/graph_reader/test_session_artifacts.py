import pathlib

import pytest

from lineapy.graph_reader.session_artifacts import SessionArtifacts
from lineapy.utils.utils import prettify


@pytest.mark.parametrize(
    "input_script, artifact_list, expected_output",
    [
        pytest.param(
            "extract_common.py",
            ["b", "c"],
            "extract_common_all.py",
            id="extract_common_all",
        ),
        pytest.param(
            "extract_common.py",
            ["b"],
            "extract_common_partial.py",
            id="extract_common_partial",
        ),
        pytest.param(
            "mutate_after_save.py",
            ["a", "b"],
            "mutate_after_save_all.py",
            id="mutate_after_save_all",
        ),
        pytest.param(
            "module_import.py",
            ["df", "df2"],
            "module_import_all.py",
            id="module_import_all",
        ),
        pytest.param(
            "module_import_alias.py",
            ["df", "df2"],
            "module_import_alias_all.py",
            id="module_import_alias_all",
        ),
        pytest.param(
            "module_import_from.py",
            ["model", "pred"],
            "module_import_from_all.py",
            id="module_import_from_all",
        ),
        pytest.param(
            "complex.py",
            ["a", "a0", "c", "f", "e", "g2", "h", "z"],
            "complex_graph_all.py",
            id="complex_graph_all",
        ),
        pytest.param(
            "complex.py",
            ["a0", "c", "h"],
            "complex_graph_a0_c_h.py",
            id="complex_graph_a0_c_h",
        ),
        pytest.param(
            "complex.py",
            ["h"],
            "complex_graph_h.py",
            id="complex_graph_h",
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
    art = res.values["art"]
    sas = SessionArtifacts([art[art_name] for art_name in artifact_list])
    refactor_result = sas.get_session_module_definition()
    expected_result = pathlib.Path(
        "tests/unit/graph_reader/expected/" + expected_output
    ).read_text()
    assert prettify(refactor_result) == prettify(expected_result)
