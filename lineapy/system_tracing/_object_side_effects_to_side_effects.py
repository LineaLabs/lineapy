from typing import Iterable, Mapping

from lineapy.data.types import LineaID
from lineapy.execution.side_effects import SideEffects
from lineapy.system_tracing._object_side_effect import ObjectSideEffect


def object_side_effects_to_side_effects(
    nodes: Mapping[LineaID, object],
    object_side_effects: Iterable[ObjectSideEffect],
) -> SideEffects:
    """
    Takes in the input nodes, as well as a number of side effects that refer to Python objects, and returns a number of
    side effects that refer to node IDs.

    It will only emit side effects that touch the input nodes,
    """
    return []
