from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List


@dataclass
class FunctionCall:
    """
    A record of a function call that happened in the tracer.
    """

    fn: Callable
    args: List[object]
    kwargs: Dict[str, object]
    res: object
