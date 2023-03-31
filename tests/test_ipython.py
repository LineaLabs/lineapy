import functools
import shutil
from typing import Callable

import pytest
from IPython.core.interactiveshell import InteractiveShell

from lineapy import save


def test_empty_cell(run_cell):
    """
    Test that the trace_line method works.
    """
    assert run_cell("") is None


def test_result(run_cell):
    assert run_cell("10") == 10

    assert run_cell("a = 10") is None
    assert run_cell("a") == 10


def test_slice(run_cell):
    assert run_cell("import lineapy") is None
    assert run_cell("a = [1, 2, 3]") is None
    assert run_cell("y = 10") is None
    assert run_cell(f"x=a[0]\na = lineapy.{save.__name__}(x, 'x')") is None

    assert run_cell("a.get_code()") == "a = [1, 2, 3]\nx = a[0]\n"


def test_slice_artifact_inline(run_cell):
    assert run_cell("import lineapy") is None
    assert run_cell("a = [1, 2, 3]\nres = lineapy.save(a, 'a')") is None
    assert (
        run_cell("res.get_code()")
        == """a = [1, 2, 3]
"""
    )


@pytest.fixture
def airflow_py_module_path(run_cell, add_config):
    assert run_cell("import lineapy") is None
    assert run_cell("a = [1, 2, 3]\nres = lineapy.save(a, 'a')") is None
    if add_config:
        to_pipeline_output = "lineapy.to_pipeline([res.name], framework='AIRFLOW', pipeline_name=res.name, output_dir='~/airflow/dags/', pipeline_dag_config={'retries': 1, 'schedule_interval': '*/30 * * * *'}).output_dir"
    else:
        to_pipeline_output = "lineapy.to_pipeline([res.name], framework='AIRFLOW', pipeline_name=res.name, output_dir='~/airflow/dags/').output_dir"

    py_module_path = run_cell(to_pipeline_output)
    yield py_module_path
    # cleanup since this tests creates files
    shutil.rmtree(py_module_path)


@pytest.mark.parametrize(
    "pipeline_file", ["a_module.py", "a_dag.py"], ids=["module", "dag"]
)
@pytest.mark.parametrize(
    "add_config", [True, False], ids=["with_config", "no_config"]
)
@pytest.mark.slow
def test_to_airflow(python_snapshot, airflow_py_module_path, pipeline_file):
    assert (
        python_snapshot == (airflow_py_module_path / pipeline_file).read_text()
    )


def test_get_value_artifact_inline(run_cell):
    assert run_cell("import lineapy") is None
    assert run_cell("a = [1, 2, 3]\nres = lineapy.save(a, 'a')") is None
    assert run_cell("res.get_value()") == [1, 2, 3]


def test_save_twice(run_cell):
    assert run_cell("import lineapy") is None
    assert run_cell("x = 100") is None
    assert run_cell("lineapy.save(x, 'x');") is None
    assert run_cell("lineapy.save(x, 'x');") is None


def test_ends_semicolon_no_print(run_cell):
    assert run_cell("10;") is None


def test_magics(run_cell):
    assert run_cell("!ls") is None


def test_artifact_codes(run_cell):
    importl = """import lineapy
"""
    code_body = """y = []
x = [y]
y.append(10)
# test comment
x[0].append(11)
print(y)
"""
    artifact_f_save = """lineapy.save(y, "deferencedy")
res = lineapy.get("deferencedy")
"""
    assert run_cell(importl) is None
    assert run_cell(code_body) is None
    assert run_cell(artifact_f_save) is None
    assert (
        run_cell("res.get_session_code()")
        == importl + code_body + artifact_f_save + "res.get_session_code()\n"
    )
    assert (
        run_cell(
            "res.db.get_session_context(res._session_id).environment_type.name"
        )
        == "JUPYTER"
    )


def test_lineapy_import_included_in_artifact(run_cell):
    code_body = """x = 1
art = lineapy.save(x,"test")
x =lineapy.get("test").get_value()
y = x +1
art2 = lineapy.save(y,"anthertest")"""
    run_cell(code_body)
    out = run_cell("art2.get_code()")
    expected = """import lineapy

x = lineapy.get("test").get_value()
y = x + 1
"""
    assert expected == out


@pytest.fixture
def ip():
    """
    Return a unique InteractiveShell instance per test.

    We call it `ip`, because that what IPython calls it in its tests.

    It provides a `run_cell` method, which returns an `ExecutionResult`.
    """
    return InteractiveShell()


@pytest.fixture
def ip_traced(ip):
    """
    An ipython fixture that first enables
    """
    assert (
        _run_cell(
            ip,
            "import lineapy.editors.ipython\nlineapy.editors.ipython.start()",
        )
        is None
    )
    return ip


def _run_cell(ip: InteractiveShell, cell: str) -> object:
    """
    Runs a cell and asserts it succeeds, returning the result.
    """

    # Set store_history to True to get execution_counts added to cells
    res = ip.run_cell(cell, store_history=True)
    if res.error_before_exec:
        raise res.error_before_exec
    if res.error_in_exec:
        raise res.error_in_exec
    return res.result


@pytest.fixture
def run_cell(ip_traced: InteractiveShell) -> Callable[[str], object]:
    return functools.partial(_run_cell, ip_traced)
