from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List


@dataclass
class FunctionCall:
    """
    A record of a function call that happened in the tracer.
    """

    fn: Callable
    args: List[object] = field(default_factory=list)
    kwargs: Dict[str, object] = field(default_factory=dict)
    res: object = field(default=None)
