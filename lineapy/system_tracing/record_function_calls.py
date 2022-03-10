from __future__ import annotations

from contextlib import contextmanager
from types import CodeType
from typing import Iterator, List

from lineapy.system_tracing.function_call import FunctionCall


@contextmanager
def record_function_calls(code: CodeType) -> Iterator[List[FunctionCall]]:
    # TODO: use tracing
    function_calls: List[FunctionCall] = []

    yield function_calls
