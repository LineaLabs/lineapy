import inspect

import pytest

from lineapy.system_tracing._op_stack import OpStack


def test_stack_access():
    f = inspect.currentframe()
    assert f
    op_stack = OpStack(f)
    with pytest.raises(IndexError):
        op_stack[-1000]
