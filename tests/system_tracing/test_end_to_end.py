"""
Test using the system tracing how it is used in the execution context, to setup some global context, call the tracing,
and then to see the results.
"""


from typing import Dict, Tuple

import pytest

from lineapy.data.types import LineaID
from lineapy.execution.globals_dict import GlobalsDict
from lineapy.execution.inspect_function import FunctionInspector
from lineapy.execution.side_effects import (
    ID,
    SideEffects,
    Variable,
    ViewOfNodes,
)
from lineapy.system_tracing.exec_and_record_function_calls import (
    exec_and_record_function_calls,
)
from lineapy.system_tracing.function_calls_to_side_effects import (
    function_calls_to_side_effects,
)


@pytest.mark.parametrize(
    "source_code,inputs,side_effects",
    [
        pytest.param(
            "for x in xs: pass",
            {"xs": ("xs_id", [[10]])},
            # x and xs should be views of each other, since modifying one can modify the other
            [ViewOfNodes([ID(LineaID("xs_id")), Variable("x")])],
            id="loop view",
            marks=pytest.mark.xfail(),
        ),
    ],
)
def test_end_to_end(
    source_code: str,
    inputs: Dict[str, Tuple[LineaID, object]],
    side_effects: SideEffects,
    function_inspector: FunctionInspector,
) -> None:
    # TODO: Refactor this and context to share more code and not duplicate this logic
    global_variables = GlobalsDict()

    global_name_to_value = {n: vs[1] for n, vs in inputs.items()}
    global_variables.setup_globals(global_name_to_value)

    code = compile(source_code, "", "exec")
    trace_fn = exec_and_record_function_calls(code, global_variables)
    assert not trace_fn.not_implemented_ops
    res = global_variables.teardown_globals()
    global_node_id_to_value = {id_: value for id_, value in inputs.values()}

    assert (
        function_calls_to_side_effects(
            function_inspector,
            trace_fn.function_calls,
            global_node_id_to_value,
            res.added_or_modified,
        )
        == side_effects
    )
