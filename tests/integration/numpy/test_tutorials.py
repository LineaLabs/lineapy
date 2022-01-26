import pathlib

import pytest

import lineapy

LINEAPY_DIR = (pathlib.Path(lineapy.__file__) / "../..").resolve()

TUTORIAL_REQUIREMENTS = (
    pathlib.Path(__file__) / "../tutorials/requirements.txt"
).resolve()


@pytest.fixture
def numpy_tutorial_virtualenv(virtualenv):

    virtualenv.run(
        f"pip install -r {TUTORIAL_REQUIREMENTS} -e {LINEAPY_DIR}",
        capture=False,
    )
    return virtualenv


def test_numpy_tutorial_env(numpy_tutorial_virtualenv):
    assert "pooch" in numpy_tutorial_virtualenv.run("pip freeze", capture=True)
