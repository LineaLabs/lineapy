from typing import Dict

import pytest

from lineapy.execution.globals_dict import GlobalsDict, GlobalsDictResult


@pytest.mark.parametrize(
    "code,inputs,accessed_inputs,added_or_modified",
    (
        pytest.param("x", {"x": 1}, ["x"], {}, id="load input"),
        pytest.param("x = 1", {}, [], {"x": 1}, id="save output"),
        pytest.param("x = 1", {"x": 2}, [], {"x": 1}, id="overwrite input"),
        pytest.param(
            "x += 1", {"x": 1}, ["x"], {"x": 2}, id="ovewrite and access input"
        ),
        pytest.param(
            "x = 2\nx", {"x": 1}, [], {"x": 2}, id="read after write"
        ),
    ),
)
def test_results(
    code: str, inputs: Dict[str, object], accessed_inputs, added_or_modified
):
    g = GlobalsDict()
    g.setup_globals(inputs)
    b = compile(code, "<string>", "exec")
    exec(b, g)
    intended_res = GlobalsDictResult(accessed_inputs, added_or_modified)
    assert g.teardown_globals() == intended_res

    # Try again to make sure it works second time
    g.setup_globals(inputs)
    exec(b, g)
    assert g.teardown_globals() == intended_res
