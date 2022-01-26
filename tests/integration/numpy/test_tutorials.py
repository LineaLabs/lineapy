import ast
import os
import pathlib
import subprocess

import astor
import pytest

import lineapy

LINEAPY_DIR = (pathlib.Path(lineapy.__file__) / "../..").resolve()

TUTORIALS = (pathlib.Path(__file__) / "../tutorials").resolve()
TUTORIAL_REQUIREMENTS = TUTORIALS / "requirements.txt"

TUTORIALS_VIRTUALENV_DIR = (
    pathlib.Path(__file__) / "../tutorial_venv"
).resolve()


@pytest.fixture(autouse=True)
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
    @pytest.mark.skip
    def test_moores_law(self):
        # This tests makes sure we can run the notebook without linea
        # We can skip it usuallyt to save time.
        subprocess.run(
            [
                "jupytext",
                "--execute",
                TUTORIALS / "content/mooreslaw-tutorial.md",
            ],
            check=True,
        )

    def test_moores_law_lineapy(self):
        os.chdir(TUTORIALS / "content")
        notebook = subprocess.run(
            [
                "jupytext",
                "mooreslaw-tutorial.md",
                "--to",
                "ipynb",
                "--out",
                "-",
            ],
            check=True,
            capture_output=True,
        ).stdout

        sliced_code = subprocess.run(
            [
                "lineapy",
                "notebook",
                "-",
                "mooreslaw_fs",
                "lineapy.file_system",
            ],
            check=True,
            capture_output=True,
            input=notebook,
        ).stdout
        sliced_path = (pathlib.Path(__file__) / "../mooreslaw_fs.py").resolve()
        desired_slice = (sliced_path).read_text()
        # Compare code by transforming both to AST, and back to source,
        # to remove comments
        assert normalize_source(sliced_code) == normalize_source(desired_slice)

        # Verify running normalized version works
        subprocess.run(["python", sliced_path], check=True)


def normalize_source(code: str) -> str:
    a = ast.parse(code)
    return astor.to_source(a)
