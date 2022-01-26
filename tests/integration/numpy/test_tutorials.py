import os
import pathlib
import subprocess
from re import sub

import pytest

import lineapy

LINEAPY_DIR = (pathlib.Path(lineapy.__file__) / "../..").resolve()

TUTORIALS = (pathlib.Path(__file__) / "../tutorials").resolve()
TUTORIAL_REQUIREMENTS = TUTORIALS / "requirements.txt"

TUTORIALS_VIRTUALENV_DIR = (
    pathlib.Path(__file__) / "../tutorial_venv"
).resolve()


@pytest.fixture(scope="session", autouse=True)
def numpy_tutorial_virtualenv():
    """
    Create a virtualenv directory for the numpy tutorial, if it doesn't exist, and prepend it to the path.
    """
    old_path = os.environ["PATH"]
    os.environ["PATH"] = (
        str(TUTORIALS_VIRTUALENV_DIR / "bin") + os.pathsep + old_path
    )
    # Remove ipythondir set for all tests, so that they are not run with linea by default
    old_ipython_dir = os.environ["IPYTHONDIR"]
    del os.environ["IPYTHONDIR"]

    if not TUTORIALS_VIRTUALENV_DIR.exists():
        subprocess.run(
            [
                "python",
                "-m",
                "venv",
                "--upgrade-deps",
                TUTORIALS_VIRTUALENV_DIR,
            ],
            check=True,
        )
        subprocess.run(
            [
                "pip",
                "install",
                "-r",
                TUTORIAL_REQUIREMENTS,
                "-e",
                LINEAPY_DIR,
                # Need nbconvert and ipyknerel for executing notebooks
                "nbconvert",
                "ipykernel",
            ],
            check=True,
        )
    yield
    os.environ["PATH"] = old_path
    os.environ["IPYTHONDIR"] = old_ipython_dir


class TestApplications:
    def test_moores_law(self):
        subprocess.run(
            [
                "jupytext",
                "--execute",
                TUTORIALS / "content/mooreslaw-tutorial.md",
            ],
            check=True,
        )

    @pytest.mark.xfail
    def test_moores_law_lineapy(self, numpy_tutorial_virtualenv):
        subprocess.run(
            [
                "lineapy",
                "jupytext",
                "--execute",
                TUTORIALS / "content/mooreslaw-tutorial.md",
            ],
            check=True,
        )
