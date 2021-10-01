import subprocess


def test_cli_entrypoint():
    """
    Verifies that the CLI command is aliased to the `lienapy` executable
    """
    subprocess.check_call(["lineapy", "--help"])


def test_slice_housing():
    """
    Verifies that the CLI command is aliased to the `lienapy` executable
    """
    subprocess.check_call(
        ["lineapy", "tests/housing.py", "--slice", "p value"]
    )
