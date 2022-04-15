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

from lineapy import save
from lineapy.data.types import SessionType
from lineapy.db.db import RelationalLineaDB
from lineapy.db.utils import (
    DB_URL_ENV_VARIABLE,
    MEMORY_DB_URL,
    resolve_default_db_path,
)
from lineapy.execution.executor import Executor
from lineapy.execution.inspect_function import FunctionInspector
from lineapy.instrumentation.tracer import Tracer
from lineapy.plugins.airflow import AirflowPlugin
from lineapy.plugins.script import ScriptPlugin
from lineapy.transformer.node_transformer import transform
from lineapy.utils.constants import DB_SQLITE_PREFIX
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.tree_logger import print_tree_log, start_tree_log
from lineapy.utils.utils import prettify
from lineapy.visualizer import Visualizer
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
    parser.addoption(
        "--tree-log",
        action="store_true",
        default=False,
        help="Log the calls as a tree",
    )


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    configure_logging()


class PythonSnapshotExtension(SingleFileSnapshotExtension):
    _file_extension = "py"

    def serialize(self, data: str, **kwargs):
        return data

    def _write_snapshot_fossil(self, snapshot_fossil: SnapshotFossil) -> None:

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
        self, snapshot_location: str, snapshot_name: str
    ) -> typing.Optional[str]:
        try:
            return Path(snapshot_location).read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

    def get_snapshot_name(self, index: int = 0) -> str:
        """
        Override to not replace < in filename
        """
        return (
            super(SingleFileSnapshotExtension, self)
            .get_snapshot_name(index=index)
            .replace("/", "__")
        )


class SVGSnapshotExtension(PythonSnapshotExtension):
    _file_extension = "svg"


@pytest.fixture
def python_snapshot(request):
    """
    Copied from the default fixture, but updating the extension class to be Python
    """
    return syrupy.SnapshotAssertion(
        update_snapshots=request.config.option.update_snapshots,
        extension_class=PythonSnapshotExtension,
        test_location=syrupy.PyTestLocation(request.node),
        session=request.session.config._syrupy,
    )


@pytest.fixture
def svg_snapshot(request):
    """
    Copied from the default fixture, but updating the extension class to be Python
    """
    return syrupy.SnapshotAssertion(
        update_snapshots=request.config.option.update_snapshots,
        extension_class=SVGSnapshotExtension,
        test_location=syrupy.PyTestLocation(request.node),
        session=request.session.config._syrupy,
    )


@pytest.fixture
def linea_db():
    return RelationalLineaDB.from_environment(MEMORY_DB_URL)


@pytest.fixture
def execute(python_snapshot, tmp_path, request, svg_snapshot, linea_db):
    """
    :param snapshot: `snapshot` is a fixture from the syrupy library that's automatically injected by pytest.
    :param tmp_path: `tmp_path` is provided by the core pytest
    :param request: `request` is provided by the core pytest
    """
    return ExecuteFixture(
        python_snapshot,
        svg_snapshot,
        tmp_path,
        request.config.getoption("--visualize"),
        linea_db,
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
    svg_snapshot: syrupy.SnapshotAssertion
    tmp_path: pathlib.Path
    # Whether to visualize the tracer graph after creating
    visualize: bool
    db: RelationalLineaDB

    def __call__(
        self,
        code: str,
        *,
        snapshot: bool = True,
        artifacts: typing.Iterable[str] = (),
    ) -> Tracer:
        """
        Tests trace, graph, and executes code on init.

        :param snapshot:  If you don't want to compare the snapshots,
        just execute the code then set `snapshot` to False.
        :param artifacts:  A list of artifacts that should be published and
        sliced based on. It assumes the artifact names are variables in the
        code.
        """
        if artifacts:
            code = "import lineapy\n" + code + "\n"
            for artifact in artifacts:
                code += (
                    f"lineapy.{save.__name__}({artifact}, {repr(artifact)})\n"
                )

        # These temp filenames are unique per test function.
        # If `execute` is called twice in a test, it will overwrite the
        # previous paths
        source_code_path = self.tmp_path / "source.py"
        source_code_path.write_text(code)

        # Verify snapshot of source of user transformed code
        tracer = Tracer(self.db, SessionType.SCRIPT)
        transform(code, source_code_path, tracer)

        if self.visualize:
            Visualizer.for_test_cli(tracer).render_pdf_file()

        # Verify snapshot of graph
        if snapshot:
            graph_str = (
                tracer.graph.print(
                    include_imports=True,
                    include_id_field=False,
                    include_session=False,
                    include_timing=False,
                )
                .replace(str(source_code_path), "[source file path]")
                .replace(
                    tracer.get_working_dir(),
                    DUMMY_WORKING_DIR,
                )
            )
            # Prettify again in case replacements cause line wraps
            assert prettify(graph_str) == self.snapshot

            # If this graph string snapshot was updated, then also update the SVG
            # snapshot. We don't want to always update the SVG snapshot, because
            # it has lots of random IDs in it. We want to use it not for testing,
            # but for better PR diffs
            res = self.snapshot._execution_results[
                self.snapshot._executions - 1
            ]

            self.svg_snapshot._update_snapshots = res.created or res.updated
            # If we aren't updating snapshots, dont even bother trying to generate the SVG
            svg_text = (
                Visualizer.for_test_snapshot(tracer).render_svg()
                if self.snapshot._update_snapshots
                else ""
            )
            svg_text == self.svg_snapshot

            # Mark the SVG snapshot as always passing
            self.svg_snapshot._execution_results[
                self.svg_snapshot._executions - 1
            ].success = True

        # Verify that execution works again, with a new session
        new_executor = Executor(self.db, globals())
        current_working_dir = os.getcwd()
        os.chdir(self.tmp_path)
        new_executor.execute_graph(tracer.graph)
        os.chdir(current_working_dir)

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


@pytest.fixture(autouse=True)
def remove_db():
    """
    Remove db before all tests
    """
    # doing this because db cleanup is only needed for sqlite
    db_url = (
        os.environ.get(DB_URL_ENV_VARIABLE, MEMORY_DB_URL) or MEMORY_DB_URL
    )
    if db_url.startswith(DB_SQLITE_PREFIX):
        p = resolve_default_db_path()
        if p.exists():
            p.unlink()


@pytest.fixture
def housing_tracer(execute):
    tests_dir = Path(__file__).parent

    # Change directory to tests dir before executing
    os.chdir(tests_dir)

    code = (tests_dir / "housing.py").read_text()
    return execute(code, snapshot=False)


@pytest.fixture
def airflow_plugin(housing_tracer):
    return AirflowPlugin(
        housing_tracer.tracer_context.db,
        housing_tracer.tracer_context.get_session_id(),
    )


@pytest.fixture
def script_plugin(housing_tracer):
    return ScriptPlugin(
        housing_tracer.tracer_context.db,
        housing_tracer.tracer_context.get_session_id(),
    )


@pytest.fixture(scope="session")
def function_inspector():
    return FunctionInspector()


@pytest.fixture(autouse=True)
def print_tree_log_fixture(request, capsys):
    if not request.config.getoption("--tree-log"):
        yield
        return
    start_tree_log(label=request.node.name)
    try:
        yield
    finally:
        # Don't capture stdout when printing, to preserve colors and column width
        with capsys.disabled():
            print_tree_log()
