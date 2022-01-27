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

    We create a custom fixture instead of using the `virtualenv` fixturte so we can cache
    the virtualenv at a relative path, to not remake it every time.
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


@pytest.mark.parametrize(
    "source_file,slice,sliced_file",
    [
        pytest.param(
            "mooreslaw-tutorial.md",
            "lineapy.file_system",
            "mooreslaw_fs.py",
            id="mooreslaw",
        ),
        pytest.param(
            "tutorial-deep-learning-on-mnist.md",
            "(weights_1, weights_2)",
            "mnist_weights.py",
            id="mnist",
            marks=pytest.mark.skip(reason="for loop, conditional"),
        ),
    ],
)
def test_tutorials(source_file, slice, sliced_file):
    os.chdir(TUTORIALS / "content")
    notebook = subprocess.run(
        [
            "jupytext",
            source_file,
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
            "{source_file}:{slice}",
            slice,
        ],
        check=True,
        capture_output=True,
        input=notebook,
    ).stdout.decode()
    sliced_path = (pathlib.Path(__file__) / ".." / sliced_file).resolve()
    desired_slice = (sliced_path).read_text()
    # Compare code by transforming both to AST, and back to source,
    # to remove comments
    assert normalize_source(sliced_code) == normalize_source(desired_slice)

    # Verify running normalized version works
    subprocess.run(["python", sliced_path], check=True)


def normalize_source(code: str) -> str:
    a = ast.parse(code)
    return astor.to_source(a)
