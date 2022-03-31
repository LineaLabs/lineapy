import logging
from typing import Iterable, Mapping

from lineapy.data.types import LineaID
from lineapy.execution.inspect_function import FunctionInspector
from lineapy.execution.side_effects import SideEffect
from lineapy.system_tracing._function_calls_to_object_side_effects import (
    function_calls_to_object_side_effects,
)
from lineapy.system_tracing._object_side_effects_to_side_effects import (
    object_side_effects_to_side_effects,
)
from lineapy.system_tracing.function_call import FunctionCall

logger = logging.getLogger(__name__)


def function_calls_to_side_effects(
    function_inspector: FunctionInspector,
    function_calls: Iterable[FunctionCall],
    input_nodes: Mapping[LineaID, object],
    output_globals: Mapping[str, object],
) -> Iterable[SideEffect]:
    """
    Translates a list of function calls to a list of side effects, by mapping objects to nodes.

    :param function_inspector: The function inspector to use to lookup what side effects each function call has.
    :param function_calls: The function calls that were recorded.
    :param input_nodes: Mapping of node ID to value for all the nodes that were passed in to this execution.
    :param output_globals: Mapping of global identifier to the value of all globals that were set during this execution.
    """
    logger.debug("Converting function calls to object side effects")

    object_side_effects = function_calls_to_object_side_effects(
        function_inspector, function_calls
    )

    logger.debug("Converting object side effects to node side effects")
    return object_side_effects_to_side_effects(
        object_side_effects, input_nodes, output_globals
    )
