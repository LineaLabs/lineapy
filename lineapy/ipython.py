"""
Code to transform inputs when running in IPython, to trace them.
"""
from __future__ import annotations
from dataclasses import field, dataclass
from typing import TYPE_CHECKING, Callable, ClassVar, Literal, Optional

from lineapy.constants import ExecutionMode
import ast
from lineapy.data.types import JupyterCell, LineaID, SessionType

from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.node_transformer import NodeTransformer


if TYPE_CHECKING:
    from IPython.core import InteractiveShell


def start(
    session_name: Optional[str] = None,
    execution_mode: ExecutionMode = ExecutionMode.MEMORY,
) -> None:
    """
    Trace any subsequent cells with linea.
    """
    ipython = get_ipython()  # type: ignore

    input_transformers_post = ipython.input_transformers_post

    linea_input_transformers = [
        it
        for it in input_transformers_post
        if isinstance(it, LineaInputTransformer)
    ]
    # TODO: Support pause/resume tracing
    assert not linea_input_transformers, "Already tracing"

    tracer = Tracer(
        SessionType.JUPYTER,
        execution_mode=execution_mode,
        session_name=session_name,
    )
    active_input_transformer = LineaInputTransformer(
        tracer, tracer.session_context.id, ipython
    )
    input_transformers_post.append(active_input_transformer)


def stop() -> Tracer:
    """
    Stop tracing.
    """
    ipython = get_ipython()  # type: ignore

    input_transformers_post = ipython.input_transformers_post

    # get the first valid input transformer and raise an error if there are more
    # than one
    (input_transformer,) = [
        it
        for it in input_transformers_post
        if isinstance(it, LineaInputTransformer)
    ]
    input_transformers_post.remove(input_transformer)
    return input_transformer.tracer


@dataclass
class LineaInputTransformer:
    tracer: Tracer
    session_id: LineaID
    ipython: InteractiveShell

    # Store the last execution count and last resulting codes lines
    # to avoid re-execution when working around an ipykernel bug
    # that calls the transformer twice TODO: make bug
    last_call: Optional[tuple[int, list[str]]] = field(default=None)

    # the last expression value execute, will be what is displayed in the cell
    last_value: object = field(default=None)

    # Mark it as having side effects so ipython doesn't try to run it on
    # completions
    # https://ipython.readthedocs.io/en/stable/config/inputtransforms.html#string-based-transformations
    has_side_effects: ClassVar[Literal[True]] = True

    def __call__(self, lines: list[str]) -> list[str]:
        """
        Translate the lines of code for the cell provided by ipython.
        """
        # TODO: better exit and stop detection
        if lines and (
            "exit()" in lines[0] or "lineapy.ipython.stop()" in lines[0]
        ):
            return lines

        execution_count = self.ipython.execution_count
        if self.last_call:
            prev_execution_count, prev_lines = self.last_call
            # Work around for ipython bug to prevent double execution in notebooks
            if execution_count == prev_execution_count:
                return prev_lines

        code = "".join(lines)
        location = JupyterCell(
            execution_count=execution_count,
            session_id=self.session_id,
        )
        node_transformer = NodeTransformer(code, location, self.tracer)
        node_transformer.visit(ast.parse(code))
        # If we hit some error while evalling, clean ourselves up and untrace
        # TODO: If linea has an error, it should unmount
        self.tracer.evaluate_records_so_far()

        self.tracer.records_manager.flush_records()

        # TODO: write to existing stdout as well when executing
        # more like tee, instead of having to write at end
        # and also remove extra spaces
        print(self.tracer.executor.get_stdout())

        # Return the last value so it will be printed, if we don't end
        # in a semicolon
        ends_with_semicolon = lines and lines[-1].endswith(";")
        if not ends_with_semicolon and node_transformer.last_statement_result:
            self.last_value = node_transformer.last_statement_result.value  # type: ignore
            lines = [
                "get_ipython().input_transformers_post[0].last_value\n",
            ]
        else:
            lines = []
        self.last_call = (execution_count, lines)
        return lines
