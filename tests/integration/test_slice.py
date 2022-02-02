import ast
import contextlib
import os
import pathlib
import subprocess
from typing import Dict, List, Union

import astor
from pytest import mark, param

INTEGRATION_DIR = pathlib.Path(__file__).parent
LINEAPY_DIR = INTEGRATION_DIR.parent.parent


# Mapping of virtualenv name to the requirements in it
VIRTUAL_ENVS: Dict[str, List[Union[str, pathlib.Path]]] = {
    "numpy-tutorials": [
        "-r",
        (INTEGRATION_DIR / "sources/numpy-tutorials/requirements.txt"),
        # Need nbconvert for executing notebooks
        "nbconvert",
    ],
    "pytorch": ["torch==1.10.2", "torchvision==0.11.3", "matplotlib"],
    # TODO: Switch this to create a conda env based on the `environment.yml`
    # in the folder
    "dask-examples": [
        "dask",
        "dask-image",
        "scikit-image",
        "numpy",
        "pandas",
        "matplotlib",
    ],
}

# A list of the params to test
PARAMS = [
    ##
    # Numpy Tutorials
    ##
    param(
        # Name of virtualenv to use
        "numpy-tutorials",
        # File to extract a slice from
        "numpy-tutorials/content/mooreslaw-tutorial.md",
        # Value to slice on
        "lineapy.file_system",
        # File with ground truth slice
        "numpy_mooreslaw_fs.py",
        # ID which is displayed in output
        id="numpy-mooreslaw",
    ),
    param(
        "numpy-tutorials",
        "numpy-tutorials/content/tutorial-deep-learning-on-mnist.md",
        "(weights_1, weights_2)",
        "numpy_mnist_weights.py",
        id="numpy-mnist",
        marks=mark.xfail(
            reason="for loop, conditional", raises=AssertionError
        ),
    ),
    param(
        "numpy-tutorials",
        "numpy-tutorials/content/tutorial-deep-reinforcement-learning-with-pong-from-pixels.md",
        "model",
        "numpy_pong_model.py",
        id="numpy-pong",
        marks=mark.xfail(reason="for loop", raises=AssertionError),
    ),
    param(
        "numpy-tutorials",
        "numpy-tutorials/content/tutorial-nlp-from-scratch.md",
        "lineapy.file_system",
        "numpy_speaches_fs.py",
        id="numpy-speaches",
        marks=mark.skip(reason="never completes"),
    ),
    param(
        "numpy-tutorials",
        "numpy-tutorials/content/tutorial-x-ray-image-processing.md",
        "lineapy.file_system",
        "numpy_x_ray_fs.py",
        id="numpy-x-ray",
        marks=mark.xfail(reason="importing submodule broken"),
    ),
    ##
    # Torch Vision
    ##
    param(
        "pytorch",
        "pytorch-vision/gallery/plot_scripted_tensor_transforms.py",
        "lineapy.file_system",
        "pytorch_plot_scripted_tensor_transforms_fs.py",
        id="pytorch-vision-tensor-transform",
        marks=mark.xfail(reason="with statement", raises=AssertionError),
    ),
    ##
    # PyTorch Tutorials
    ##
    param(
        "pytorch",
        "pytorch-tutorials/beginner_source/Intro_to_TorchScript_tutorial.py",
        "lineapy.file_system",
        "pytorch-intro-torchscript.py",
        id="pytorch-tutorial-intro-torchscript",
        marks=mark.xfail(reason="class statement", raises=AssertionError),
    ),
    ##
    # Dask Examples
    ##
    param(
        "dask-examples",
        "dask-examples/applications/image-processing.ipynb",
        "lineapy.file_system",
        "dask_examples_image_processing.py",
        id="dask_examples_image_processing",
        marks=mark.xfail(reason="importing submodule broken"),
    ),
]


@mark.integration
@mark.parametrize("venv,source_file,slice_value,sliced_file", PARAMS)
def test_slice(
    venv: str, source_file: str, slice_value: str, sliced_file: str, request
) -> None:
    with use_virtualenv(venv):
        sliced_code = slice_file(
            source_file, slice_value, request.config.getoption("--visualize")
        )

        # Verify running manually sliced version works
        sliced_path = INTEGRATION_DIR / "slices" / sliced_file
        # Run with ipython so `get_ipython()` is available for sliced magics
        subprocess.run(["ipython", sliced_path], check=True)
        desired_slice = sliced_path.read_text()

        # Compare normalized sliced
        assert normalize_source(sliced_code) == normalize_source(desired_slice)


def slice_file(source_file: str, slice_value: str, visualize: bool) -> str:
    """
    Slices the file for the value and returns the code
    """
    resolved_source_path = INTEGRATION_DIR / "sources" / source_file
    os.chdir(resolved_source_path.parent)

    file_ending = resolved_source_path.suffix
    file_name = resolved_source_path.name

    artifact_name = f"{source_file}:{slice}"

    additional_args: List[Union[str, pathlib.Path]] = (
        [
            "--visualize-slice",
            LINEAPY_DIR / "out.pdf",
        ]
        if visualize
        else []
    )

    if file_ending == ".py":
        args = [
            "lineapy",
            "file",
            file_name,
            artifact_name,
            slice_value,
            *additional_args,
        ]

        return subprocess.run(
            args, check=True, stdout=subprocess.PIPE
        ).stdout.decode()
    elif file_ending == ".md":
        # To run a jupytext markdown file,
        # first convert to notebook then pipe to runing the notebook
        notebook = subprocess.run(
            [
                "jupytext",
                file_name,
                "--to",
                "ipynb",
                "--out",
                "-",
            ],
            check=True,
            stdout=subprocess.PIPE,
        ).stdout

        args = [
            "lineapy",
            "notebook",
            "-",
            artifact_name,
            slice_value,
            *additional_args,
        ]

        return subprocess.run(
            args, check=True, stdout=subprocess.PIPE, input=notebook
        ).stdout.decode()
    elif file_ending == ".ipynb":
        args = [
            "lineapy",
            "notebook",
            file_name,
            artifact_name,
            slice_value,
            *additional_args,
        ]

        return subprocess.run(
            args, check=True, stdout=subprocess.PIPE
        ).stdout.decode()
    else:
        raise NotImplementedError()


@contextlib.contextmanager
def use_virtualenv(name: str):
    """
    Activates the virtualenv with NAME, creating it if it does not exist.

    On exit of the context manager, it resets the path and ipython directory.
    """
    virtualenv_dir = INTEGRATION_DIR / "venvs" / name
    old_path = os.environ["PATH"]
    os.environ["PATH"] = str(virtualenv_dir / "bin") + os.pathsep + old_path
    # Remove ipythondir set for all tests, so that they are not run with linea by default
    old_ipython_dir = os.environ["IPYTHONDIR"]
    del os.environ["IPYTHONDIR"]
    try:
        if not virtualenv_dir.exists():
            subprocess.run(
                [
                    "python",
                    "-m",
                    "venv",
                    virtualenv_dir,
                ],
                check=True,
            )
            subprocess.run(
                [
                    "pip",
                    "install",
                    # Include ipython as well so we can use it to test the slice
                    "ipython",
                    "ipykernel",
                    # Include Jupyter Lab so we can launch from venv to test things manually
                    "jupyterlab",
                    "-e",
                    LINEAPY_DIR,
                    *VIRTUAL_ENVS[name],
                ],
                check=True,
            )
        yield
    finally:
        os.environ["PATH"] = old_path
        os.environ["IPYTHONDIR"] = old_ipython_dir


def normalize_source(code: str) -> str:
    """
    Normalize the source code by going to and from AST, to remove all formatting and comments
    """
    a = ast.parse(code)
    return astor.to_source(a)
