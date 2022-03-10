from typing import Iterable, Mapping

from lineapy.data.types import LineaID
from lineapy.execution.side_effects import SideEffects
from lineapy.system_tracing._object_side_effect import ObjectSideEffect


def object_side_effects_to_side_effects(
    nodes: Mapping[LineaID, object],
    object_side_effects: Iterable[ObjectSideEffect],
) -> SideEffects:
    return []
