from typing import Dict, List, Mapping

import pytest

from lineapy.data.types import LineaID
from lineapy.execution.side_effects import (
    ID,
    SideEffects,
    Variable,
    ViewOfNodes,
)
from lineapy.system_tracing.function_call import FunctionCall
from lineapy.system_tracing.function_calls_to_side_effects import (
    function_calls_to_side_effects,
)

inner_l = [100]
outer_l = [inner_l]
iter_l = iter(outer_l)


@pytest.mark.parametrize(
    "function_calls,input_nodes,output_globals,side_effects",
    [
        pytest.param(
            [
                FunctionCall(iter, [[1, 2]], {}, iter_l),
                FunctionCall(next, [iter_l], {}, inner_l),
            ],
            {"l_id": outer_l},
            {"i": inner_l},
            [ViewOfNodes([ID(LineaID("l_id")), Variable("i")])],
            id="iter view",
            marks=pytest.mark.xfail(),
        ),
    ],
)
def test_function_calls_to_side_effects(
    function_calls: List[FunctionCall],
    input_nodes: Dict[LineaID, object],
    output_globals: Mapping[str, object],
    side_effects: SideEffects,
    function_inspector,
):
    assert (
        function_calls_to_side_effects(
            function_inspector,
            function_calls,
            input_nodes,
            output_globals,
        )
        == side_effects
    )
