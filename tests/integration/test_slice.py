from __future__ import annotations

import ast
import contextlib
import logging
import os
import pathlib
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

import astor
import yaml
from pytest import mark, param

from lineapy.utils.logging_config import LOGGING_ENV_VARIABLE
from lineapy.utils.utils import prettify

INTEGRATION_DIR = pathlib.Path(__file__).parent
LINEAPY_DIR = INTEGRATION_DIR.parent.parent


@dataclass
class Environment:
    # List of args to pass to pip install
    pip: list[str] = field(default_factory=list)
    # Extra conda channels to add
    conda_channels: list[str] = field(default_factory=list)
    # The conda environment file to use
    conda_env: Optional[Path] = None
    # List of additional conda packages to install
    conda_deps: list[str] = field(default_factory=list)


logger = logging.getLogger(__name__)

# Mapping of the environment name to the environment with the requirements in it.
# Also allow a thunk to the Environment, so that the value is not evaluated
# until the test is run, so that if the sources are not available this won't
# trigger an error if these tests are skipped
ENVS: Dict[str, Union[Environment, Callable[[], Environment]]] = {
    "numpy-tutorials": Environment(
        conda_env=(
            INTEGRATION_DIR / "sources/numpy-tutorials/environment.yml"
        ),
        conda_deps=["cmake"],
    ),
    "pytorch": lambda: Environment(
        conda_deps=["torchvision=0.11.3"],
        conda_channels=["pytorch"],
        pip=[
            line
            for line in (
                INTEGRATION_DIR
                / "sources/pytorch-tutorials/.devcontainer/requirements.txt"
            )
            .read_text()
            .splitlines()
            if (
                line
                and not line.startswith("#")
                # remove awscli dependency because its incompatible with recent rich version
                and "awscli" not in line
                # Make sure we use the conda version of torchvision, otherwise get bus error
                and "torchvision" not in line
            )
        ],
    ),
    "dask-examples": Environment(
        conda_env=(
            INTEGRATION_DIR / "sources/dask-examples/binder/environment.yml"
        ),
    ),
    "tensorflow-docs": Environment(
        conda_deps=["tensorflow=2.6", "matplotlib", "pillow", "numpy"],
        pip=["tensorflow_hub"],
    ),
    "xgboost": Environment(
        conda_deps=["xgboost", "scikit-learn", "numpy", "scipy"]
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
        marks=mark.xfail(
            reason="slice within for loop", raises=AssertionError
        ),
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
        marks=mark.xfail(
            reason="slice part of with statement",
            raises=AssertionError,
        ),
    ),
    ##
    # PyTorch Tutorials
    ##
    param(
        "pytorch",
        "pytorch-tutorials/beginner_source/Intro_to_TorchScript_tutorial.py",
        "lineapy.file_system",
        id="pytorch_intro_torchscript",
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
        marks=mark.xfail(reason="cant pickle tensorflow model"),
    ),
    param(
        "tensorflow-docs",
        "tensorflow-docs/site/en/tutorials/structured_data/preprocessing_layers.ipynb",
        "lineapy.file_system",
        id="tensorflow_preprocessing_layers",
    ),
    param(
        "tensorflow-docs",
        "tensorflow-decision-forests/documentation/tutorials/beginner_colab.ipynb",
        "lineapy.file_system",
        id="tensorflow_decision_forests_beginner",
        marks=mark.xfail(
            reason="cant install tensorflow_decision_forests on mac"
        ),
    ),
    param(
        "tensorflow-docs",
        "tensorflow-docs/site/en/tutorials/load_data/csv.ipynb",
        "lineapy.file_system",
        id="tensorflow_load_csv",
        marks=mark.xfail(reason="import error"),
    ),
    param(
        "tensorflow-docs",
        "tensorflow-docs/site/en/tutorials/keras/regression.ipynb",
        "lineapy.file_system",
        id="tensorflow_regression",
        marks=mark.xfail(reason="time magic"),
    ),
    param(
        "tensorflow-docs",
        "tensorflow-docs/site/en/tutorials/images/transfer_learning_with_hub.ipynb",
        "lineapy.file_system",
        id="tensorflow_transfer_hub",
    ),
    ##
    # XGBoost
    ##
    param(
        "xgboost",
        "xgboost/demo/guide-python/sklearn_examples.py",
        "lineapy.file_system",
        id="xgboost_sklearn_examples",
        marks=mark.xfail(reason="garbage collection"),
    ),
    param(
        "xgboost",
        "xgboost/demo/guide-python/basic_walkthrough.py",
        "lineapy.file_system",
        id="xgboost_basic_walkthrough",
        marks=mark.xfail(reason="import error"),
    ),
]


@mark.integration
@mark.parametrize("env,source_file,slice_value", PARAMS)
def test_slice(
    request, env: str, source_file: str, slice_value: str, python_snapshot
) -> None:
    with use_env(env):

        # change to source directory
        resolved_source_path = INTEGRATION_DIR / "sources" / source_file
        source_dir = resolved_source_path.parent
        os.chdir(source_dir)

        # Get manually sliced version
        test_id = request.node.callspec.id
        sliced_path = INTEGRATION_DIR / f"slices/{test_id}.py"
        # If the sliced file does not exist, copy the source file to it
        if not sliced_path.exists():
            logger.info(
                "Copying file to slice %s. Manually edit this slice.",
                sliced_path,
            )
            write_python_file(resolved_source_path, sliced_path)

        desired_slice = normalize_source(sliced_path.read_text())

        # Overwrite the manual slice with the transformed code and a header
        header = (
            f"# This is the manual slice of:\n"
            f"#  {slice_value}\n"
            "# from file:\n"
            f"#  sources/{source_file}\n"
            "\n"
            "# To verify that linea produces the same slice, run:\n"
            f"#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[{test_id}]'\n\n"
        )
        sliced_file_contents = header + desired_slice
        sliced_path.write_text(sliced_file_contents)
        logger.info("Writing slice to %s", sliced_path)

        # Verify that manually sliced version works
        # Run with ipython so `get_ipython()` is available for sliced magics
        # Copy to file in source directory, so __file__ resolves properly in sliced code
        with tempfile.NamedTemporaryFile(
            dir=source_dir, suffix=".py"
        ) as tmp_file:
            logger.info("Running tmp copy of slice at %s", tmp_file.name)
            tmp_file.write(sliced_file_contents.encode())
            tmp_file.flush()
            run_and_log("ipython", tmp_file.name)

        # Slice the file with lineapy
        logger.info("Running lineapy to slice %s", resolved_source_path)
        sliced_code = slice_file(
            resolved_source_path,
            slice_value,
            request.config.getoption("--visualize"),
        )
        normalized_slice = normalize_source(sliced_code)

        # Save snapshot of normalized slice, so that the current state is committed to source
        assert normalized_slice == python_snapshot

        # Verify slice is the same as desired slice
        assert normalized_slice == desired_slice


def slice_file(source_path: Path, slice_value: str, visualize: bool) -> str:
    """
    Slices the file for the value and returns the code
    """

    file_ending = source_path.suffix
    file_name = source_path.name

    artifact_name = f"{file_name}:{slice_value}"

    # Set logging to be more detailed, in case problems arise

    additional_args: List[Union[str, pathlib.Path]] = (
        [
            "--visualize-slice",
            LINEAPY_DIR / "out",
        ]
        if visualize
        else []
    )

    if file_ending == ".py":
        return run_and_log(
            "lineapy",
            "file",
            file_name,
            artifact_name,
            slice_value,
            *additional_args,
            stdout=subprocess.PIPE,
        ).stdout
    elif file_ending == ".md":
        # To run a jupytext markdown file, first convert to notebook then run the notebook with lineapy
        notebook_file = tempfile.NamedTemporaryFile(
            delete=False, suffix=".ipynb"
        ).name
        run_and_log(
            "jupytext",
            file_name,
            "--to",
            "ipynb",
            "--out",
            notebook_file,
        )

        return run_and_log(
            "lineapy",
            "notebook",
            notebook_file,
            artifact_name,
            slice_value,
            *additional_args,
            stdout=subprocess.PIPE,
        ).stdout
    elif file_ending == ".ipynb":

        return run_and_log(
            "lineapy",
            "notebook",
            file_name,
            artifact_name,
            slice_value,
            *additional_args,
            stdout=subprocess.PIPE,
        ).stdout
    else:
        raise NotImplementedError()


def write_python_file(
    source_path: pathlib.Path, target_path: pathlib.Path
) -> None:
    """
    Loads the source path and writes it as a Python file to the target path.
    """
    file_ending = source_path.suffix
    if file_ending == ".py":
        target_path.write_text(source_path.read_text())
    elif file_ending == ".ipynb":
        run_and_log(
            "jupyter",
            "nbconvert",
            "--to",
            "python",
            source_path,
            "--output-dir",
            target_path.parent,
            "--output",
            target_path.name,
        )
    else:
        raise NotImplementedError()


def run_and_log(*args, **kwargs) -> subprocess.CompletedProcess[str]:
    # Set lineapy subprocesses to have more verbose logging
    env = {**os.environ, LOGGING_ENV_VARIABLE: "INFO"}
    logger.info("Calling %s", " ".join(map(str, args)))
    return subprocess.run(args, check=True, env=env, text=True, **kwargs)


@contextlib.contextmanager
def use_env(name: str):
    """
    Activates the conda environment with NAME, creating it if it does not exist.

    On exit of the context manager, it resets the path and ipython directory.
    """
    env = ENVS[name]
    if callable(env):
        env = env()
    env_dir = INTEGRATION_DIR / "envs" / name

    old_path = os.environ["PATH"]
    os.environ["PATH"] = str(env_dir / "bin") + os.pathsep + old_path
    # Remove ipythondir set for all tests, so that they are not run with linea by default
    old_ipython_dir = os.environ["IPYTHONDIR"]
    del os.environ["IPYTHONDIR"]

    try:
        if env_dir.exists():
            logger.info("Using previously created env %s", env_dir)
        else:
            env_file = create_env_file(env)
            logger.info("Creating env from generated file: %s", env_file)
            run_and_log(
                "conda", "env", "create", "-f", env_file, "-p", env_dir, "-v"
            )
            env_file.unlink()
        yield
    finally:
        os.environ["PATH"] = old_path
        os.environ["IPYTHONDIR"] = old_ipython_dir


def normalize_source(code: str) -> str:
    """
    Normalize the source code by going to and from AST, to remove all formatting and comments,
    then prettifying with black.
    """
    a = ast.parse(code)
    return prettify(astor.to_source(a))


def create_env_file(env: Environment) -> Path:
    """
    Creates a temporary env file with these dependencies as well as the default ones required for lineapy.
    """
    channels: list[str] = [*env.conda_channels, "conda-forge"]
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
        "ipykernel",
        "pip",
        *env.conda_deps,
    ]
    pip_dependencies = [f"-e {LINEAPY_DIR}", *env.pip]
    if env.conda_env:
        loaded_conda_env = yaml.safe_load(env.conda_env.read_text())
        for c in loaded_conda_env.get("channels", []):
            if c not in channels:
                channels.insert(0, c)
        for dep in loaded_conda_env.get("dependencies", []):
            if isinstance(dep, str):
                dependencies.append(dep)
            # If the dependency is a dict, assume its a pip list of requirements
            elif isinstance(dep, dict):
                pip_dependencies.extend(dep["pip"])
            else:
                raise NotImplementedError()
    yaml_file = {
        "channels": channels,
        "dependencies": [*dependencies, {"pip": pip_dependencies}],
    }
    fd, path = tempfile.mkstemp(
        text=True,
        suffix=".yaml",
        # Create it in the same directory as the conda env file, if we used one,
        # so that relative paths in the conda env to `requirements.txt` files
        # are resolved properly
        dir=env.conda_env.parent if env.conda_env else None,
    )
    with os.fdopen(fd, "w") as fp:
        yaml.dump(yaml_file, fp)
    return Path(path)
