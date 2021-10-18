import subprocess


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
