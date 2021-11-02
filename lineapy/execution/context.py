"""
This module contains a number of globals, which are set by the execution when its
processing nodes. 
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from lineapy.data.types import CallNode
    from lineapy.execution.executor import Executor


class RecordGetitemDict(dict):
    """
    A custom dict that records which keys have been succesfully accessed.

    We cannot overload the `__setitem__` method, since Python will not respect
    it for custom globals, but we can overload the __getitem__ method.

    See https://stackoverflow.com/a/12185315/907060
    which refers to https://bugs.python.org/issue14385
    """

    def __init__(self, *args, **kwargs):
        self._getitems: list[str] = []
        super().__init__(*args, **kwargs)

    def __getitem__(self, k):
        r = super().__getitem__(k)
        if k not in self._getitems:
            self._getitems.append(k)
        return r


# A mapping of all the global variables available to the call.
GLOBAL_VARIABLES = RecordGetitemDict()

# The current node we are processing
NODE: Optional[CallNode] = None

# The current tracer we are using
EXECUTOR: Optional[Executor] = None
