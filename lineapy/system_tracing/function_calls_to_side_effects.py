from typing import Iterable, Mapping

from lineapy.data.types import LineaID
from lineapy.execution.inspect_function import FunctionInspector
from lineapy.execution.side_effects import SideEffects
from lineapy.system_tracing._function_calls_to_object_side_effects import (
    function_calls_to_object_side_effects,
)
from lineapy.system_tracing._object_side_effects_to_side_effects import (
    object_side_effects_to_side_effects,
)
from lineapy.system_tracing.function_call import FunctionCall


def function_calls_to_side_effects(
    function_inspector: FunctionInspector,
    function_calls: Iterable[FunctionCall],
    nodes: Mapping[LineaID, object],
) -> SideEffects:
    object_side_effects = function_calls_to_object_side_effects(
        function_inspector, function_calls
    )
    return object_side_effects_to_side_effects(nodes, object_side_effects)
