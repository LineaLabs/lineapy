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


class WrongSlice(Exception):
    """
    Raised when the slice was incorrect. Used to differentiate that and failing on not being able to slice
    at all, or not being able to execute the sliced notebook
    """

    pass


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


@pytest.mark.integration
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
            marks=pytest.mark.xfail(
                reason="for loop, conditional", raises=WrongSlice
            ),
        ),
        pytest.param(
            "tutorial-deep-reinforcement-learning-with-pong-from-pixels.md",
            "model",
            "pong_model.py",
            id="pong",
            marks=pytest.mark.xfail(reason="for loop", raises=WrongSlice),
        ),
        pytest.param(
            "tutorial-nlp-from-scratch.md",
            "lineapy.file_system",
            "speaches_fs.py",
            id="speaches",
            marks=pytest.mark.skip(reason="never completes"),
        ),
        pytest.param(
            "tutorial-x-ray-image-processing.md",
            "lineapy.file_system",
            "x_ray_fs.py",
            id="x-ray",
            marks=pytest.mark.xfail(reason="importing submodule broken"),
        ),
    ],
)
def test_tutorials(request, source_file, slice, sliced_file):

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
        stdout=subprocess.PIPE,
    ).stdout

    args = ["lineapy", "notebook", "-", "{source_file}:{slice}", slice]
    # If you pass the --visualize flag to pytest, then output a visualize of the slice to `out.pdf`
    if request.config.getoption("--visualize"):
        args += [
            "--visualize-slice",
            LINEAPY_DIR / "out.pdf",
        ]

    sliced_code = subprocess.run(
        args, check=True, stdout=subprocess.PIPE, input=notebook
    ).stdout.decode()
    sliced_path = (pathlib.Path(__file__) / ".." / sliced_file).resolve()

    # Verify running normalized version works
    subprocess.run(["python", sliced_path], check=True)

    desired_slice = sliced_path.read_text()
    try:
        # Compare code by transforming both to AST, and back to source,
        # to remove comments
        assert normalize_source(sliced_code) == normalize_source(desired_slice)
    except AssertionError:
        raise WrongSlice()


def normalize_source(code: str) -> str:
    a = ast.parse(code)
    return astor.to_source(a)
