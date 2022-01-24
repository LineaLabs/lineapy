from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Union


class TRACER_EVENTS(Enum):
    CALL = "CALL"
    TRACEIMPORT = "TIMPORT"
    VISUALIZE = "visualize"


@dataclass
class GlobalContext(ABC):
    def notify(
        self, operator: object, event: Union[None, TRACER_EVENTS]
    ) -> None:
        pass
