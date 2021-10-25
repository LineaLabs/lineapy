import subprocess

import pytest


def test_cli_entrypoint():
    """
    Verifies that the "--help" CLI command is aliased to the `lienapy` executable
    """
    subprocess.check_call(["lineapy", "--help"])


def test_slice_housing():
    """
    Verifies that the "--slice" CLI command is aliased to the `lienapy` executable
    """
    subprocess.check_call(
        ["lineapy", "tests/housing.py", "--slice", "p value"]
    )


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


def test_kaggle_example1():

    subprocess.check_call(
        [
            "lineapy",
            "examples/kaggle_example1.py",
            "--slice",
            "mushroom feature importance",
        ]
    )


@pytest.mark.xfail(reason="lambdas aren't supported")
def test_kaggle_example2():

    subprocess.check_call(
        [
            "lineapy",
            "examples/kaggle_example2.py",
            "--slice",
            "nn for diabetes",
        ]
    )


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
