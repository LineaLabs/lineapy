from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class FunctionCall:
    """
    A record of a function call that happened in the tracer.
    """

    fn: Callable
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    res: Any = field(default=None)
