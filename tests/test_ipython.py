from IPython.core.interactiveshell import InteractiveShell, ExecutionResult
import pytest


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
    res = ip.run_cell("import lineapy.ipython\nlineapy.ipython.start()")
    assert res.success
    assert res.result is None
    return ip


def assert_success(res: ExecutionResult, result=None) -> None:
    assert not res.error_before_exec
    assert not res.error_in_exec
    assert res.result == result


def test_run_cell(ip):
    """
    Test that the run_cell method works.
    """
    assert_success(ip.run_cell("a = 1; 10"), 10)
    assert ip.user_ns["a"] == 1


def test_empty_cell(ip_traced):
    """
    Test that the trace_line method works.
    """
    assert_success(ip_traced.run_cell(""))


def test_result(ip_traced):
    assert_success(ip_traced.run_cell("10"), 10)


def test_assign(ip_traced):
    assert_success(ip_traced.run_cell("a = 10"))
    assert_success(ip_traced.run_cell("a"), 10)
