import subprocess
import tempfile

import pytest


@pytest.mark.slow
def test_cli_entrypoint():
    """
    Verifies that the "--help" CLI command is aliased to the `lineapy` executable
    """
    subprocess.check_call(["lineapy", "--help"])


@pytest.mark.slow
def test_pass_arg():
    """
    Verifies that the arg is pass into the command
    """
    code = """import sys
import lineapy
lineapy.save(sys.argv[1], "first_arg")"""
    with tempfile.NamedTemporaryFile() as f:
        f.write(code.encode())
        f.flush()
        subprocess.check_call(
            [
                "lineapy",
                "python",
                f.name,
                "--slice",
                "first_arg",
                "--arg",
                "an arg",
            ]
        )


@pytest.mark.slow
def test_slice_housing():
    """
    Verifies that the "--slice" CLI command is aliased to the `lineapy` executable
    """
    subprocess.check_call(
        ["lineapy", "python", "tests/housing.py", "--slice", "p value"]
    )


@pytest.mark.slow
def test_slice_housing_multiple():
    """
    Verifies that we can run "--slice" CLI command multiple times
    """
    subprocess.check_call(
        [
            "lineapy",
            "python",
            "tests/housing.py",
            "--slice",
            "p value",
            "--slice",
            "y",
        ]
    )


@pytest.mark.slow
def test_export_slice_housing():
    """
    Verifies that the "--export-slice" CLI command is aliased to the `lineapy` executable
    """
    subprocess.check_call(
        [
            "lineapy",
            "python",
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
            "python",
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

    linea_run = subprocess.run(
        ["lineapy", "python", str(f)], capture_output=True
    )
    python_run = subprocess.run(["python", str(f)], capture_output=True)
    assert linea_run.returncode == python_run.returncode
    assert linea_run.stdout.decode() == python_run.stdout.decode()
    assert linea_run.stderr.decode() == python_run.stderr.decode()


def test_ipython():
    code = 'import lineapy; print(lineapy.save(1, "one").get_code())'
    res = subprocess.check_output(["lineapy", "ipython", "-c", code])
    assert res.decode().strip().endswith(code)
