"""
Code to transform inputs when running in IPython, to trace them.
"""
from __future__ import annotations
from dataclasses import field
from typing import TYPE_CHECKING, Callable, ClassVar, Literal, Optional

from attr import dataclass, has
from lineapy.constants import ExecutionMode
import ast
from lineapy.data.types import JupyterCell, LineaID, SessionType

from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.node_transformer import NodeTransformer


if TYPE_CHECKING:
    from IPython.core import InteractiveShell


# TODO: Support starting, stopping, and restarting.
def start(
    session_name: Optional[str] = None,
    execution_mode: ExecutionMode = ExecutionMode.MEMORY,
) -> None:
    """
    Trace any subsequent cells with linea.
    """
    ipython = get_ipython()  # type: ignore

    input_transformers_post: list[
        Callable[[list[str]], list[str]]
    ] = ipython.input_transformers_post

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

    input_transformers_post: list[
        Callable[[list[str]], list[str]]
    ] = ipython.input_transformers_post

    linea_input_transformers = [
        it
        for it in input_transformers_post
        if isinstance(it, LineaInputTransformer)
    ]
    assert len(linea_input_transformers) == 1, "Not tracing"
    return linea_input_transformers[0].tracer


@dataclass
class LineaInputTransformer:
    tracer: Tracer
    session_id: LineaID
    ipython: InteractiveShell

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

        ends_with_semicolon = lines and lines[-1].endswith(";")
        code = "".join(lines)
        location = JupyterCell(
            execution_count=self.ipython.execution_count,
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
        if not ends_with_semicolon and node_transformer.last_statement_result:
            self.last_value = node_transformer.last_statement_result.value  # type: ignore
            return [
                "get_ipython().input_transformers_post[0].last_value\n",
            ]
        return []
