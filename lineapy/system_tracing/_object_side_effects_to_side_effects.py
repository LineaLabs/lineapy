from typing import Iterable, Mapping

from lineapy.data.types import LineaID
from lineapy.execution.side_effects import SideEffects
from lineapy.system_tracing._object_side_effect import ObjectSideEffect


def object_side_effects_to_side_effects(
    object_side_effects: Iterable[ObjectSideEffect],
    input_nodes: Mapping[LineaID, object],
    output_globals: Mapping[str, object],
) -> SideEffects:
    """
    Translates a list of object side effects to a list of side effects, by mapping objects to nodes, and only emitting side effects
    which relate to either the input nodes or the output globals.

    :param object_side_effects: The object side effects that were recorded.
    :param input_nodes: Mapping of node ID to value for all the nodes that were passed in to this execution.
    :param output_globals: Mapping of global identifier to the value of all globals that were set during this execution.
    """
    # TODO: Use Variable(k) to represent output nodes
    return []
