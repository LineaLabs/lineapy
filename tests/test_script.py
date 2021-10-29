import subprocess

import pytest


@pytest.mark.slow
def test_cli_entrypoint():
    """
    Verifies that the "--help" CLI command is aliased to the `lienapy` executable
    """
    subprocess.check_call(["lineapy", "--help"])


@pytest.mark.slow
def test_slice_housing():
    """
    Verifies that the "--slice" CLI command is aliased to the `lienapy` executable
    """
    subprocess.check_call(
        ["lineapy", "tests/housing.py", "--slice", "p value"]
    )


@pytest.mark.slow
def test_export_slice_housing():
    """
    Verifies that the "--export-slice" CLI command is aliased to the `lienapy` executable
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
def test_kaggle_example1():

    subprocess.check_call(
        [
            "lineapy",
            "examples/kaggle_example1.py",
            "--slice",
            "mushroom feature importance",
        ]
    )


@pytest.mark.slow
def test_kaggle_example2():

    subprocess.check_call(
        [
            "lineapy",
            "examples/kaggle_example2.py",
            "--slice",
            "nn for diabetes",
        ]
    )


@pytest.mark.parametrize(
    "code",
    ("+++", "1 / 0", "1\nx"),
    ids=("syntax error", "runtime error", "name error"),
)
def test_linea_python_equivalent(tmp_path, code):
    """
    Verifies that Python and lineapy have the same output.
    """
    f = tmp_path / "script.py"
    f.write_text(code)

    linea_run = subprocess.run(["lineapy", str(f)], capture_output=True)
    python_run = subprocess.run(["python", str(f)], capture_output=True)
    assert linea_run.returncode == python_run.returncode
    assert linea_run.stdout.decode() == python_run.stdout.decode()
    assert linea_run.stderr.decode() == python_run.stderr.decode()


@pytest.mark.skip(reason="https://github.com/LineaLabs/lineapy/issues/341")
def test_run_from_nbconvert():
    # delete viz first, if it exists (-f exits cleanly either way)
    subprocess.check_call(["rm", "-f", "tests/tmp.pdf"])
    # Run the command that should populate the database
    subprocess.check_call(
        "env LINEA_VISUALIZATION_NAME=tmp jupyter nbconvert --to notebook --execute tests/untraced_notebook.ipynb --inplace --ExecutePreprocessor.extra_arguments=--IPKernelApp.extensions=lineapy --debug".split(
            " "
        )
    )
    # Delete it after (will exit cleanly only if it existed)
    subprocess.check_call(["rm", "tests/tmp.pdf"])
