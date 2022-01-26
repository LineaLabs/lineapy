import pathlib

import pytest

import lineapy

LINEAPY_DIR = (pathlib.Path(lineapy.__file__) / "../..").resolve()

TUTORIALS = (pathlib.Path(__file__) / "../tutorials").resolve()
TUTORIAL_REQUIREMENTS = TUTORIALS / "requirements.txt"


@pytest.fixture(scope="function")
def numpy_tutorial_virtualenv(virtualenv):

    virtualenv.run(
        # Need nbconvert and ipyknerel for executing notebooks
        f"pip install -r {TUTORIAL_REQUIREMENTS} -e {LINEAPY_DIR} nbconvert ipykernel",
        capture=False,
    )
    return virtualenv


class TestApplications:
    def test_moores_law(self, numpy_tutorial_virtualenv):
        numpy_tutorial_virtualenv.run(
            f"jupytext --execute {TUTORIALS/ 'content/mooreslaw-tutorial.md'}",
            capture=False,
        )

    @pytest.mark.xfail
    def test_moores_law_lineapy(self, numpy_tutorial_virtualenv):
        numpy_tutorial_virtualenv.run(
            f"lineapy jupytext --execute {TUTORIALS/ 'content/mooreslaw-tutorial.md'}",
            capture=False,
        )
