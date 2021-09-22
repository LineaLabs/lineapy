from __future__ import annotations
import datetime
import dataclasses
from lineapy.graph_writer.graph_printer import GraphPrinter
import pathlib
import typing
from pathlib import Path
import black

import pytest
import pytest_subtests
import syrupy
from syrupy.data import SnapshotFossil
from syrupy.extensions.single_file import SingleFileSnapshotExtension

from lineapy.constants import ExecutionMode
from lineapy.data.graph import Graph
from lineapy.data.types import Artifact, SessionContext, SessionType
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.execution.executor import Executor
from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.transformer import Transformer


# Based off of unmerged JSON extension
# Writes each snapshot to its own Python file
# https://github.com/tophat/syrupy/pull/552/files#diff-9bab2a0973c5e73c86ed7042300befcaa5a034df17cea4d013eeaece6af66979
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
def execute(snapshot, subtests, tmp_path):
    return ExecuteFixture(
        lambda: snapshot(extension_class=PythonSnapshotExtension),
        subtests,
        tmp_path,
    )


@dataclasses.dataclass
class ExecuteFixture:
    """
    Creates an instance returned from the fixture.

    Like https://docs.pytest.org/en/6.2.x/fixture.html#factories-as-fixtures but uses a class with a __call__ method,
    instead of a function, for better debugging.
    """

    make_snapshot: typing.Callable[[], syrupy.SnapshotAssertion]
    subtests: pytest_subtests.SubTests
    tmp_path: pathlib.Path

    def __call__(
        self,
        code: str,
        *,
        exec_transformed_xfail: str = None,
        session_type: SessionType = SessionType.SCRIPT,
    ):
        """
        Tests trace, graph, and executes code on init.

        If exec_transformed_xfail is passed in, then will expect the execution of the transformed code to fail.
        https://docs.pytest.org/en/latest/how-to/skipping.html#xfail-mark-test-functions-as-expected-to-fail

        If you don't want to execute, you can set the session type to STATIC
        """
        transformer = Transformer()
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

        with self.subtests.test(msg="node transformer"):
            # Replace the source path with a consistant name so its compared properly
            pretty_trace_code = black.format_str(
                trace_code.replace(
                    str(source_code_path), "[source file path]"
                ),
                mode=black.Mode(),
            )
            assert pretty_trace_code == self.make_snapshot()

        if exec_transformed_xfail is not None:
            pytest.xfail(exec_transformed_xfail)
            return

        transformed_code_path = self.tmp_path / "transformed.py"

        # Write to tmp file before execing, b/c it looks at file
        transformed_code_path.write_text(trace_code)

        # Execute the transformed code to create the graph in memory and exec
        locals: dict[str, typing.Any] = {}
        with self.subtests.test(msg="exec transformed"):
            bytecode = compile(trace_code, str(transformed_code_path), "exec")
            exec(bytecode, {}, locals)
        tracer: Tracer = locals["lineapy_tracer"]

        db = tracer.records_manager.db

        # Verify snapshot of graph
        nodes = db.get_all_nodes()
        graph = Graph(nodes)
        context = SessionContext.from_orm(
            db.get_context_by_file_name(session_name)
        )

        with self.subtests.test(msg="graph"):

            assert (
                GraphPrinter(graph, context)()
                .replace(str(source_code_path), "[source file path]")
                .replace(
                    repr(context.creation_time),
                    repr(datetime.datetime.fromordinal(1)),
                )
                == self.make_snapshot()
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

    def slice(self, variable_name: str) -> ExecuteResult:
        pass
        # TODO: implement like:
        #         graph, context = self.write_and_read_graph(
        #     graph_with_messy_nodes, graph_with_messy_nodes_session
        # )
        # self.lineadb.add_node_id_to_artifact_table(
        #     f_assign.id,
        #     get_current_time(),
        # )
        # result = self.lineadb.get_graph_from_artifact_id(f_assign.id)
        # self.lineadb.remove_node_id_from_artifact_table(f_assign.id)
        # e = Executor()
        # e.execute_program(result, context)
        # f = e.get_value_by_variable_name("f")
        # assert f == 6
        # assert are_graphs_identical(result, graph_sliced_by_var_f)
