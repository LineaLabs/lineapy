import subprocess

import pytest


@pytest.mark.slow
def test_cli_entrypoint():
    """
    Verifies that the "--help" CLI command is aliased to the `lineapy` executable
    """
    subprocess.check_call(["lineapy", "--help"])


@pytest.mark.slow
def test_slice_housing():
    """
    Verifies that the "--slice" CLI command is aliased to the `lineapy` executable
    """
    subprocess.check_call(
        ["lineapy", "tests/housing.py", "--slice", "p value"]
    )


@pytest.mark.slow
def test_slice_housing_multiple():
    """
    Verifies that we can run "--slice" CLI command multiple times
    """
    subprocess.check_call(
        ["lineapy", "tests/housing.py", "--slice", "p value", "--slice", "y"]
    )


@pytest.mark.slow
def test_export_slice_housing():
    """
    Verifies that the "--export-slice" CLI command is aliased to the `lineapy` executable
    """
    subprocess.check_call(
        [
            "lineapy",
            "tests/housing.py",
            "--slice",
            "p value",
            "--export-slice",
            "sliced_housing",
        ]
    )


@pytest.mark.slow
def test_export_slice_housing_multiple():
    """
    Verifies that we can run "--export-slice" CLI command multiple times
    """
    subprocess.check_call(
        [
            "lineapy",
            "tests/housing.py",
            "--slice",
            "p value",
            "--export-slice",
            "p_value_housing",
            "--slice",
            "y",
            "--export-slice",
            "y_housing",
        ]
    )


@pytest.mark.parametrize(
    "code",
    (
        "+++",
        "1 / 0",
        "1\nx",
        "import lineapy.utils.__error_on_load",
        "import lineapy_xxx",
    ),
    ids=(
        "syntax error",
        "runtime error",
        "name error",
        "error in import",
        "invalid import",
    ),
)
def test_linea_python_equivalent(tmp_path, code):
    """
    Verifies that Python and lineapy have the same stack trace.
    """
    f = tmp_path / "script.py"
    f.write_text(code)

    linea_run = subprocess.run(["lineapy", str(f)], capture_output=True)
    python_run = subprocess.run(["python", str(f)], capture_output=True)
    assert linea_run.returncode == python_run.returncode
    assert linea_run.stdout.decode() == python_run.stdout.decode()
    assert linea_run.stderr.decode() == python_run.stderr.decode()
