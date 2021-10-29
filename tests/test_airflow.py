import subprocess

import pytest


@pytest.mark.slow
@pytest.mark.airflowtest
def test_export_slice_housing_dag():
    """
    Verifies that the "--airflow" CLI command produces a working Airflow DAG
    """
    subprocess.check_call(
        [
            "lineapy",
            "tests/housing.py",
            "--slice",
            "p value",
            "--airflow",
            "sliced_housing_dag",
        ]
    )
    subprocess.check_call(
        [
            "airflow",
            "db",
            "init",
        ]
    )
    subprocess.check_call(
        [
            "airflow",
            "dags",
            "test",
            "sliced_housing_dag_dag",
            "2020-10-19",
            "-S",
            ".",
        ]
    )
