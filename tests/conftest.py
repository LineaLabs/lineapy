from __future__ import annotations
import datetime
import dataclasses
from lineapy.graph_reader.program_slice import get_program_slice
from lineapy.db.relational.schema.relational import ArtifactORM
import os
import pathlib
import typing
from pathlib import Path

import pytest
from sqlalchemy import true
import syrupy
from syrupy.data import SnapshotFossil
from syrupy.extensions.single_file import SingleFileSnapshotExtension

from lineapy.constants import ExecutionMode
from lineapy.data.graph import Graph
from lineapy.data.types import Artifact, SessionType
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.execution.executor import Executor
from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.transformer import Transformer
from lineapy.graph_reader.program_slice import get_program_slice
from lineapy.utils import prettify
from .util import get_project_directory

# Based off of unmerged JSON extension
# Writes each snapshot to its own Python file
# https://github.com/tophat/syrupy/pull/552/files#diff-9bab2a0973c5e73c86ed7042300befcaa5a034df17cea4d013eeaece6af66979

DUMMY_WORKING_DIR = "dummy_linea_repo/"


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
    return syrupy.SnapshotAssertion(
        update_snapshots=request.config.option.update_snapshots,
        extension_class=PythonSnapshotExtension,
        test_location=syrupy.PyTestLocation(request.node),
        session=request.session.config._syrupy,
    )


@pytest.fixture
def execute(python_snapshot, tmp_path):
    """
    :param snapshot: `snapshot` is a fixture from the syrupy library that's automatically injected by pytest.
    :param tmp_path: `tmp_path` is provided by the core pytest
    """
    return ExecuteFixture(
        python_snapshot,
        tmp_path,
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

    def __call__(
        self,
        code: str,
        *,
        exec_transformed_xfail: str = None,
        session_type: SessionType = SessionType.SCRIPT,
        compare_snapshot: bool = True,
    ):
        """
        Tests trace, graph, and executes code on init.

        All kwargs are keyword only (`*`)

        :param exec_transformed_xfail: If `exec_transformed_xfail` is passed in
        then we will expect the execution of the transformed code to fail.

        :param session_type:  If you don't want to execute, you can set the
        `session_type` to STATIC

        :param compare_snapshot:  If you don't want to compare the snapshots,
        just execute the code then set `compare_snapshot` to False.
        """
        transformer = Transformer()
        # These temp filenames are unique per test function.
        # If `execute` is called twice in a test, it will overwrite the
        # previous paths
        source_code_path = self.tmp_path / "source.py"
        source_code_path.write_text(code)

        # Verify snapshot of source of user transformed code

        session_name = str(source_code_path)
        trace_code = transformer.transform(
            code,  # Set as script so it evals
            session_type=session_type,
            # TODO: rename arg to session path
            session_name=session_name,
            execution_mode=ExecutionMode.MEMORY,
        )

        # Replace the source path with a consistant name so its compared properly
        pretty_trace_code = prettify(
            trace_code.replace(str(source_code_path), "[source file path]"),
        )
        if compare_snapshot:
            assert pretty_trace_code == self.snapshot

        if exec_transformed_xfail is not None:
            pytest.xfail(exec_transformed_xfail)

        transformed_code_path = self.tmp_path / "transformed.py"

        # Write to tmp file before execing, b/c it looks at file
        transformed_code_path.write_text(trace_code)

        # Execute the transformed code to create the graph in memory and exec
        locals: dict[str, typing.Any] = {}
        bytecode = compile(trace_code, str(transformed_code_path), "exec")

        exec(bytecode, {}, locals)

        tracer: Tracer = locals["lineapy_tracer"]

        db = tracer.records_manager.db

        # Verify snapshot of graph
        nodes = db.get_all_nodes()
        context = db.get_context_by_file_name(session_name)
        graph = Graph(nodes, context)
        if compare_snapshot:
            assert (
                graph.printer()
                .replace(str(source_code_path), "[source file path]")
                .replace(
                    repr(context.creation_time),
                    repr(datetime.datetime.fromordinal(1)),
                )
                .replace(
                    context.working_directory,
                    DUMMY_WORKING_DIR,
                )
                == self.snapshot
            )

        return ExecuteResult(db, graph, tracer.executor)


@dataclasses.dataclass
class ExecuteResult:
    db: RelationalLineaDB
    graph: Graph
    executor: Executor

    @property
    def values(self) -> dict[str, object]:
        return self.executor._variable_values

    @property
    def stdout(self) -> str:
        return self.executor.get_stdout()

    @property
    def artifacts(self) -> list[Artifact]:
        return self.db.get_all_artifacts()

    def slice(self, artifact_name: str) -> str:
        """
        Gets the code for a slice of the graph from an artifact
        """
        artifact = (
            self.db.session.query(ArtifactORM)
            .filter(ArtifactORM.name == artifact_name)
            .one()
        )
        return get_program_slice(self.graph, [artifact.id])


@pytest.fixture(autouse=True)
def chdir_test_file():
    """
    Make sure all tests are run relative to the project root
    """
    current_working_dir = os.getcwd()

    os.chdir(get_project_directory())
    yield
    os.chdir(current_working_dir)
