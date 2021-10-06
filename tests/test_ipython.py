from typing import Callable
from IPython.core.interactiveshell import InteractiveShell, ExecutionResult
import pytest
import functools
from lineapy.instrumentation.tracer import Tracer


def test_empty_cell(run_cell):
    """
    Test that the trace_line method works.
    """
    assert run_cell("") is None


def test_result(run_cell):
    assert run_cell("10") == 10


def test_assign(run_cell):
    assert run_cell("a = 10") is None
    assert run_cell("a") == 10


def test_stop(run_cell):
    assert isinstance(run_cell("lineapy.ipython.stop()"), Tracer)
    assert run_cell("10") == 10


def test_slice(run_cell):
    assert run_cell("import lineapy") is None
    assert run_cell("a = [1, 2, 3]") is None
    assert run_cell("y = 10") is None
    assert run_cell("x=a[0]\nlineapy.linea_publish(x, 'x')") is None
    assert (
        run_cell("tracer = lineapy.ipython.stop()\ntracer.slice('x')")
        == "a = [1, 2, 3]\nx=a[0]\n"
    )


@pytest.fixture
def ip():
    """
    Return a unique InteractiveShell instance per test.

    We call it `ip`, because that what IPython calls it in its tests.

    It provides a `run_cell` method, which returns an `ExecutionResult`.
    """
    shell = InteractiveShell()
    yield shell


@pytest.fixture
def ip_traced(ip):
    """
    An ipython fixture that first enables
    """
    assert (
        _run_cell(ip, "import lineapy.ipython\nlineapy.ipython.start()")
        is None
    )
    return ip


def _run_cell(ip: InteractiveShell, cell: str) -> object:
    """
    Runs a cell and asserts it succeeds, returning the result.
    """
    res = ip.run_cell(cell)
    assert not res.error_before_exec
    assert not res.error_in_exec
    return res.result


@pytest.fixture
def run_cell(ip_traced: InteractiveShell) -> Callable[[str], object]:
    return functools.partial(_run_cell, ip_traced)
