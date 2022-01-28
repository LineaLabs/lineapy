import ast
import os
import pathlib
import subprocess
import typing

import astor

import lineapy

LINEAPY_DIR = (pathlib.Path(lineapy.__file__) / "../..").resolve()


def get_slice_path(name: str) -> pathlib.Path:
    return (pathlib.Path(__file__) / "../slices" / name).resolve()


def get_source_path(name: str) -> pathlib.Path:
    return (pathlib.Path(__file__) / "../sources" / name).resolve()


class WrongSlice(Exception):
    """
    Raised when the slice was incorrect. Used to differentiate that and failing on not being able to slice
    at all, or not being able to execute the sliced notebook
    """

    pass


def normalize_source(code: str) -> str:
    """
    Normalize the source code by going to and from AST, to remove all formatting and comments
    """
    a = ast.parse(code)
    return astor.to_source(a)


def create_virtualenv(
    name: str, additional_pip_install_args: typing.List[str]
):
    """
    Create a virtualenv directory, if it doesn't exist, and prepend the bin it to the path.

    We create a custom fixture instead of using the `virtualenv` fixturte so we can cache
    the virtualenv at a relative path, to not remake it every time.
    """
    virtualenv_dir = (pathlib.Path(__file__) / "../venvs" / name).resolve()
    old_path = os.environ["PATH"]
    os.environ["PATH"] = str(virtualenv_dir / "bin") + os.pathsep + old_path
    # Remove ipythondir set for all tests, so that they are not run with linea by default
    old_ipython_dir = os.environ["IPYTHONDIR"]
    del os.environ["IPYTHONDIR"]

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
                "-e",
                LINEAPY_DIR,
                *additional_pip_install_args,
            ],
            check=True,
        )
    yield
    os.environ["PATH"] = old_path
    os.environ["IPYTHONDIR"] = old_ipython_dir
