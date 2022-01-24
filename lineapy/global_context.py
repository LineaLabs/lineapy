from __future__ import annotations

from abc import ABC
from dataclasses import InitVar, dataclass, field
from enum import Enum
from typing import Dict, Union

from lineapy.data.types import Node, SessionType


class TRACER_EVENTS(Enum):
    CALL = "CALL"
    TRACEIMPORT = "TIMPORT"
    VISUALIZE = "visualize"


class IPYTHON_EVENTS(Enum):
    StartedState = "StartedState"
    CellsExecutedState = "CellsExecutedState"


@dataclass
class GlobalContext(ABC):
    session_type: InitVar[SessionType]
    variable_name_to_node: Dict[str, Node] = field(
        default_factory=dict, init=False
    )

    def notify(
        self,
        operator: object,
        event: Union[None, TRACER_EVENTS, IPYTHON_EVENTS],
        *args,
        **kwargs
    ) -> None:
        pass
