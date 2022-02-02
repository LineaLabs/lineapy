from __future__ import annotations

import ast
import contextlib
import os
import pathlib
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

import astor
import yaml
from pytest import mark, param

INTEGRATION_DIR = pathlib.Path(__file__).parent
LINEAPY_DIR = INTEGRATION_DIR.parent.parent


@dataclass
class Environment:
    # List of args to pass to pip install ...
    pip: list[str] = field(default_factory=list)
    # The conda environment file to use
    conda_env: Optional[Path] = None
    # List of additional conda packages to install
    conda_deps: list[str] = field(default_factory=list)


# Mapping of the environment name to the requirements in it
ENVS: Dict[str, Environment] = {
    "numpy-tutorials": Environment(
        conda_env=(
            INTEGRATION_DIR / "sources/numpy-tutorials/environment.yml"
        ),
        conda_deps=[
            "cmake",
            # Add this as conda arg to help with version resolution till https://github.com/numpy/numpy-tutorials/pull/125 is merged
            "jupyter-book",
        ],
    ),
    "pytorch": Environment(
        pip=[
            f"-r {INTEGRATION_DIR / 'sources/pytorch-tutorials/requirements.txt'}",
        ]
    ),
    "dask-examples": Environment(
        conda_env=(
            INTEGRATION_DIR / "sources/dask-examples/binder/environment.yml"
        ),
    ),
    "tensorflow-docs": Environment(
        conda_deps=["tensorflow", "matplotlib", "pillow", "numpy"]
    ),
}

# A list of the params to test
PARAMS = [
    ##
    # Numpy Tutorials
    ##
    param(
        # Name of environment to use
        "numpy-tutorials",
        # File to extract a slice from
        "numpy-tutorials/content/mooreslaw-tutorial.md",
        # Value to slice on
        "lineapy.file_system",
        # ID which is displayed in output and used to lookup the slice file
        id="numpy_mooreslaw",
    ),
    param(
        "numpy-tutorials",
        "numpy-tutorials/content/tutorial-deep-learning-on-mnist.md",
        "(weights_1, weights_2)",
        id="numpy_mnist",
        marks=mark.xfail(
            reason="for loop, conditional", raises=AssertionError
        ),
    ),
    param(
        "numpy-tutorials",
        "numpy-tutorials/content/tutorial-deep-reinforcement-learning-with-pong-from-pixels.md",
        "model",
        id="numpy_pong",
        marks=mark.xfail(reason="for loop", raises=AssertionError),
    ),
    param(
        "numpy-tutorials",
        "numpy-tutorials/content/tutorial-nlp-from-scratch.md",
        "lineapy.file_system",
        id="numpy_speaches",
        marks=mark.skip(reason="never completes"),
    ),
    param(
        "numpy-tutorials",
        "numpy-tutorials/content/tutorial-x-ray-image-processing.md",
        "lineapy.file_system",
        id="numpy_x_ray",
        marks=mark.xfail(reason="importing submodule broken"),
    ),
    ##
    # Torch Vision
    ##
    param(
        "pytorch",
        "pytorch-vision/gallery/plot_scripted_tensor_transforms.py",
        "lineapy.file_system",
        id="pytorch_vision_tensor_transform",
        marks=mark.xfail(reason="with statement", raises=AssertionError),
    ),
    ##
    # PyTorch Tutorials
    ##
    param(
        "pytorch",
        "pytorch-tutorials/beginner_source/Intro_to_TorchScript_tutorial.py",
        "lineapy.file_system",
        id="pytorch_intro_torchscript",
        marks=mark.xfail(reason="class statement", raises=AssertionError),
    ),
    ##
    # Dask Examples
    ##
    param(
        "dask-examples",
        "dask-examples/applications/image-processing.ipynb",
        "lineapy.file_system",
        id="dask_examples_image_processing",
        marks=mark.xfail(reason="importing submodule broken"),
    ),
    ##
    # Tensorflow Docs
    ##
    param(
        "tensorflow-docs",
        "tensorflow-docs/site/en/tutorials/images/classification.ipynb",
        "model",
        id="tensorflow_image_classification",
        # marks=mark.xfail(reason="cant install"),
    ),
]


@mark.integration
@mark.parametrize("env,source_file,slice_value", PARAMS)
def test_slice(request, env: str, source_file: str, slice_value: str) -> None:
    with use_env(env):
        sliced_code = slice_file(
            source_file, slice_value, request.config.getoption("--visualize")
        )

        # Verify running manually sliced version works
        sliced_path = INTEGRATION_DIR / f"slices/{request.node.callspec.id}.py"
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

    artifact_name = f"{source_file}:{slice_value}"

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
def use_env(name: str):
    """
    Activates the conda environment with NAME, creating it if it does not exist.

    On exit of the context manager, it resets the path and ipython directory.
    """
    env = ENVS[name]
    env_dir = INTEGRATION_DIR / "envs" / name

    old_path = os.environ["PATH"]
    os.environ["PATH"] = str(env_dir / "bin") + os.pathsep + old_path
    # Remove ipythondir set for all tests, so that they are not run with linea by default
    old_ipython_dir = os.environ["IPYTHONDIR"]
    del os.environ["IPYTHONDIR"]

    try:
        if env_dir.exists():
            print(f"Using previously created env {env_dir}")
        else:
            env_file = create_env_file(env)
            print(f"Creating env from generated file: {env_file}")
            subprocess.run(
                [
                    "conda",
                    "env",
                    "create",
                    "--verbose",
                    "-f",
                    env_file,
                    "-p",
                    env_dir,
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


def create_env_file(env: Environment) -> Path:
    """
    Creates a temporary env file with these dependencies as well as the default ones required for lineapy.
    """
    channels: set[str] = {"conda-forge"}
    # Start with all lineapy deps
    dependencies: list[str] = [
        # Downgrade jupyter client https://github.com/jupyter/jupyter_console/issues/241
        "jupyter_client=6.1.12",
        "python>=3.7,<3.10",
        "Pillow",
        "astor",
        "click>=8.0.0",
        "pydantic",
        "SQLAlchemy",
        "networkx",
        "black",
        "rich",
        "astpretty",
        "scour=0.38.2",
        "pyyaml",
        "asttokens",
        "isort",
        "graphviz",
        "IPython",
        "jinja2",
        "nbformat",
        "nbconvert",
        *env.conda_deps,
    ]
    pip_dependencies = [f"-e {LINEAPY_DIR}", *env.pip]
    if env.conda_env:
        loaded_conda_env = yaml.safe_load(env.conda_env.read_text())
        channels.update(loaded_conda_env.get("channels", []))
        for dep in loaded_conda_env.get("dependencies", []):
            if isinstance(dep, str):
                dependencies.append(dep)
            # If the dependency is a dict, assume its a pip list of requirements
            elif isinstance(dep, dict):
                pip_dependencies.extend(dep["pip"])
            else:
                raise NotImplementedError()
    yaml_file = {
        "channels": list(channels),
        "dependencies": [*dependencies, {"pip": pip_dependencies}],
    }
    fd, path = tempfile.mkstemp(text=True, suffix=".yaml")
    with os.fdopen(fd, "w") as fp:
        yaml.dump(yaml_file, fp)
    return Path(path)
