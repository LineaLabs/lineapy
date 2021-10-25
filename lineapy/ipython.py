"""
Code to transform inputs when running in IPython, to trace them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Literal, Optional

from lineapy.constants import ExecutionMode
from lineapy.data.types import JupyterCell, LineaID, SessionType
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.node_transformer import transform

if TYPE_CHECKING:
    from IPython.core import InteractiveShell


def start(
    session_name: Optional[str] = None,
    execution_mode: ExecutionMode = ExecutionMode.MEMORY,
    ipython: Optional[InteractiveShell] = None,
) -> None:
    """
    Trace any subsequent cells with linea.
    """
    ipython = ipython or get_ipython()  # type: ignore

    input_transformers_post = ipython.input_transformers_post

    linea_input_transformers = [
        it
        for it in input_transformers_post
        if isinstance(it, LineaInputTransformer)
    ]
    # TODO: Support pause/resume tracing
    assert not linea_input_transformers, "Already tracing"

    db = RelationalLineaDB.from_environment(execution_mode)
    tracer = Tracer(db, SessionType.JUPYTER, session_name)
    active_input_transformer = LineaInputTransformer(
        tracer, tracer.session_context.id, ipython
    )
    input_transformers_post.append(active_input_transformer)


def stop(
    ipython: Optional[InteractiveShell] = None,
    visualization_filename: Optional[str] = None,
) -> Tracer:
    """
    Stop tracing. If "visualization_filename" is passed, will use that as the filename
    to save the visualization to, appending the file extension.
    """
    ipython = ipython or get_ipython()  # type: ignore

    input_transformers_post = ipython.input_transformers_post

    # get the first valid input transformer and raise an error if there are more
    # than one
    (input_transformer,) = [
        it
        for it in input_transformers_post
        if isinstance(it, LineaInputTransformer)
    ]
    tracer = input_transformer.tracer
    if visualization_filename:
        tracer.visualize(visualization_filename)
    tracer.db.close()
    input_transformers_post.remove(input_transformer)
    return tracer


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
        last_node = transform(code, location, self.tracer)

        # TODO: write to existing stdout as well when executing
        # more like tee, instead of having to write at end
        # and also remove extra spaces
        print(self.tracer.executor.get_stdout())

        # Return the last value so it will be printed, if we don't end
        # in a semicolon
        ends_with_semicolon = lines and lines[-1].endswith(";")
        if not ends_with_semicolon and last_node:
            self.last_value = self.tracer.executor.get_value(last_node)
            # We are adding the following lines to the transpiled python code
            #   it's a little hacky right now since we rely on others not
            #   having any input_transformers (hence the `[0]`).
            # The `last_value` is tracked by this class, `LineaInputTransformer`.
            lines = [
                "get_ipython().input_transformers_post[0].last_value\n",
            ]
        else:
            lines = []
        self.last_call = (execution_count, lines)
        return lines
