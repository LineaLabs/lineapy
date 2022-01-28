import os
import pathlib
import subprocess

import pytest

import lineapy

from .utils import (
    WrongSlice,
    create_virtualenv,
    get_slice_path,
    get_source_path,
    normalize_source,
)

LINEAPY_DIR = (pathlib.Path(lineapy.__file__) / "../..").resolve()

TUTORIALS = get_source_path("numpy-tutorials")
TUTORIAL_REQUIREMENTS = TUTORIALS / "requirements.txt"


@pytest.fixture(autouse=True)
def numpy_tutorial_virtualenv():
    yield from create_virtualenv(
        "numpy-tutorials",
        [
            "-r",
            str(TUTORIAL_REQUIREMENTS),
            # Need nbconvert and ipyknerel for executing notebooks
            "nbconvert",
            "ipykernel",
        ],
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "source_file,slice,sliced_file",
    [
        pytest.param(
            "mooreslaw-tutorial.md",
            "lineapy.file_system",
            "numpy_mooreslaw_fs.py",
            id="mooreslaw",
        ),
        pytest.param(
            "tutorial-deep-learning-on-mnist.md",
            "(weights_1, weights_2)",
            "numpy_mnist_weights.py",
            id="mnist",
            marks=pytest.mark.xfail(
                reason="for loop, conditional", raises=WrongSlice
            ),
        ),
        pytest.param(
            "tutorial-deep-reinforcement-learning-with-pong-from-pixels.md",
            "model",
            "numpy_pong_model.py",
            id="pong",
            marks=pytest.mark.xfail(reason="for loop", raises=WrongSlice),
        ),
        pytest.param(
            "tutorial-nlp-from-scratch.md",
            "lineapy.file_system",
            "numpy_speaches_fs.py",
            id="speaches",
            marks=pytest.mark.skip(reason="never completes"),
        ),
        pytest.param(
            "tutorial-x-ray-image-processing.md",
            "lineapy.file_system",
            "numpy_x_ray_fs.py",
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
    sliced_path = get_slice_path(sliced_file)

    # Verify running normalized version works
    subprocess.run(["python", sliced_path], check=True)

    desired_slice = sliced_path.read_text()
    try:
        # Compare code by transforming both to AST, and back to source,
        # to remove comments
        assert normalize_source(sliced_code) == normalize_source(desired_slice)
    except AssertionError:
        raise WrongSlice()
