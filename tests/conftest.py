from __future__ import annotations

import dataclasses
import os
import pathlib
import typing
from pathlib import Path

import pytest
import syrupy
from syrupy.data import SnapshotFossil
from syrupy.extensions.single_file import SingleFileSnapshotExtension

from lineapy.constants import ExecutionMode
from lineapy.data.types import SessionType
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.execution.executor import Executor
from lineapy.instrumentation.tracer import Tracer
from lineapy.logging import configure_logging
from lineapy.transformer.node_transformer import transform
from lineapy.utils import prettify
from lineapy.visualizer.visual_graph import VisualGraphOptions
from tests.util import get_project_directory

# Based off of unmerged JSON extension
# Writes each snapshot to its own Python file
# https://github.com/tophat/syrupy/pull/552/files#diff-9bab2a0973c5e73c86ed7042300befcaa5a034df17cea4d013eeaece6af66979

DUMMY_WORKING_DIR = "dummy_linea_repo/"


def pytest_addoption(parser):
    parser.addoption(
        "--visualize",
        action="store_true",
        default=False,
        help="Visualize the tracer sessions",
    )


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    configure_logging("INFO")


class PythonSnapshotExtension(SingleFileSnapshotExtension):
    _file_extension = "py"

    def serialize(self, data: str, **kwargs) -> str:  # type: ignore
        return data

    def _write_snapshot_fossil(
        self, *, snapshot_fossil: SnapshotFossil
    ) -> None:

        filepath, data = (
            snapshot_fossil.location,
            next(iter(snapshot_fossil)).data,
        )
        if not isinstance(data, str):
            error_text = "Can't write into a file. Expected '{}', got '{}'"
            raise TypeError(
                error_text.format(str.__name__, type(data).__name__)
            )
        Path(filepath).write_text(data, encoding="utf-8")

    def _read_snapshot_data_from_location(
        self, *, snapshot_location: str, snapshot_name: str
    ) -> typing.Optional[str]:
        try:
            return Path(snapshot_location).read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

    def get_snapshot_name(self, *, index: int = 0) -> str:
        """
        Override to not replace < in filename
        """
        return (
            super(SingleFileSnapshotExtension, self)
            .get_snapshot_name(index=index)
            .replace("/", "__")
        )


@pytest.fixture
def python_snapshot(request):
    """
    Copied from the default fixture, but updating the extension class to be Python
    """
    return syrupy.SnapshotAssertion(  # type: ignore
        update_snapshots=request.config.option.update_snapshots,
        extension_class=PythonSnapshotExtension,
        test_location=syrupy.PyTestLocation(request.node),  # type: ignore
        session=request.session.config._syrupy,
    )


@pytest.fixture
def execute(python_snapshot, tmp_path, request):
    """
    :param snapshot: `snapshot` is a fixture from the syrupy library that's automatically injected by pytest.
    :param tmp_path: `tmp_path` is provided by the core pytest
    :param request: `request` is provided by the core pytest
    """
    return ExecuteFixture(
        python_snapshot, tmp_path, request.config.getoption("--visualize")
    )


@dataclasses.dataclass
class ExecuteFixture:
    """
    Creates an instance returned from the fixture.

    Like https://docs.pytest.org/en/6.2.x/fixture.html#factories-as-fixtures
    but uses a class with a __call__ method, instead of a function, for
    better debugging.
    """

    snapshot: syrupy.SnapshotAssertion
    tmp_path: pathlib.Path
    # Whether to visualize the tracer graph after creating
    visualize: bool

    def __call__(
        self,
        code: str,
        *,
        compare_snapshot: bool = True,
        artifacts: typing.Iterable[str] = (),
    ) -> Tracer:
        """
        Tests trace, graph, and executes code on init.

        :param compare_snapshot:  If you don't want to compare the snapshots,
        just execute the code then set `compare_snapshot` to False.
        :param artifacts:  A list of artifacts that should be published and
        sliced based on. It assumes the artifact names are variables in the
        code.
        """
        if artifacts:
            code = "import lineapy\n" + code + "\n"
            for artifact in artifacts:
                code += (
                    f"lineapy.linea_publish({artifact}, {repr(artifact)})\n"
                )

        # These temp filenames are unique per test function.
        # If `execute` is called twice in a test, it will overwrite the
        # previous paths
        source_code_path = self.tmp_path / "source.py"
        source_code_path.write_text(code)

        # Verify snapshot of source of user transformed code
        db = RelationalLineaDB.from_environment(ExecutionMode.MEMORY)
        tracer = Tracer(db, SessionType.SCRIPT)
        transform(code, source_code_path, tracer)

        if self.visualize:
            tracer.visualize(
                options=VisualGraphOptions(
                    show_view_and_mutation_tracking=True
                )
            )

        # Verify snapshot of graph
        if compare_snapshot:
            graph_str = (
                tracer.graph.print(
                    include_imports=True,
                    include_id_field=False,
                    include_session=False,
                    include_timing=False,
                )
                .replace(str(source_code_path), "[source file path]")
                .replace(
                    tracer.session_context.working_directory,
                    DUMMY_WORKING_DIR,
                )
            )
            # Prettify again in case replacements cause line wraps
            assert prettify(graph_str) == self.snapshot

        # Verify that execution works again, loading from the DB, in a new dir
        new_executor = Executor(db)
        os.chdir(self.tmp_path)
        new_executor.execute_graph(tracer.graph)

        return tracer


@pytest.fixture(autouse=True)
def chdir_test_file():
    """
    Make sure all tests are run relative to the project root
    """
    current_working_dir = os.getcwd()

    os.chdir(get_project_directory())
    yield
    os.chdir(current_working_dir)


@pytest.fixture
def assertionist():
    def _tester(actual, asserts):
        for (asserttype, varname, expectedvalue) in asserts:
            if asserttype == "value":
                assert actual.values[varname] == expectedvalue
            elif asserttype == "classname":
                assert (
                    actual.values[varname].__class__.__name__ == expectedvalue
                )
            elif asserttype == "valuearray":
                assert (actual.values[varname] == expectedvalue).all()
            elif asserttype == "artifact":
                assert actual.artifacts[varname] == expectedvalue

    return _tester
