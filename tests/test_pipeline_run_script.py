import os
import subprocess

import pytest


@pytest.mark.slow
def test_run_script_dag(virtualenv, tmp_path):
    """
    Verifies that the DAGs we produce do run successfully.
    """

    # FIXME - we need a more basic test than this that does not depend on pandas and sklearn etc.
    # installing them takes way too long right now.

    # Copy the dag and the data
    # NOTE: Don't want to leave them in the tests folder, since there are other
    # files we need to copy without which the dag will fail.
    subprocess.check_call(
        [
            "cp",
            "-f",
            "tests/unit/plugins/expected/script_pipeline_housing_simple/script_pipeline_housing_simple_module.py",
            str(tmp_path),
        ]
    )

    os.chdir(str(tmp_path))

    subprocess.check_call(
        ["python", "script_pipeline_housing_simple_module.py"]
    )
