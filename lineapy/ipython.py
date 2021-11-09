"""
Code to transform inputs when running in IPython, to trace them.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import ClassVar, Literal, Optional

from IPython.core.interactiveshell import InteractiveShell
from IPython.display import SVG, DisplayHandle, display

from lineapy.data.types import JupyterCell, LineaID, SessionType
from lineapy.db.db import RelationalLineaDB
from lineapy.exceptions.excepthook import transform_except_hook_args
from lineapy.exceptions.flag import REWRITE_EXCEPTIONS
from lineapy.exceptions.user_exception import AddFrame
from lineapy.instrumentation.tracer import Tracer
from lineapy.ipython_cell_storage import cleanup_cells, get_cell_path
from lineapy.logging import configure_logging
from lineapy.transformer.node_transformer import transform


def start(
    session_name: Optional[str] = None,
    db_url: Optional[str] = None,
    visualize=False,
    ipython: Optional[InteractiveShell] = None,
) -> None:
    """
    Trace any subsequent cells with linea.
    """
    configure_logging("INFO")
    ipython = ipython or get_ipython()  # type: ignore

    # Ipython does not use exceptionhook, so instead we monkeypatch
    # how it processes the exceptions, in order to add our handler
    # that removes the outer frames.
    if REWRITE_EXCEPTIONS:
        InteractiveShell._get_exc_info = custom_get_exc_info

    input_transformers_post = ipython.input_transformers_post

    linea_input_transformers = [
        it
        for it in input_transformers_post
        if isinstance(it, LineaInputTransformer)
    ]
    # TODO: Support pause/resume tracing
    assert not linea_input_transformers, "Already tracing"

    db = RelationalLineaDB.from_environment(db_url)
    tracer = Tracer(db, SessionType.JUPYTER, session_name)

    # Create a display handler so that we can update the SVG visualization
    # after each cell
    # https://web.archive.org/web/20211025232037/https://mindtrove.info/jupyter-tidbit-display-handles/
    display_handle = (
        display(SVG(tracer.visualize_to_svg()), display_id=True)
        if visualize
        else None
    )

    active_input_transformer = LineaInputTransformer(
        tracer, tracer.session_context.id, ipython, display_handle
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

    # Remove the cells we stored
    cleanup_cells()
    # Reset the exception handling
    InteractiveShell._get_exc_info = original_get_exc_info

    return tracer


@dataclass
class LineaInputTransformer:
    tracer: Tracer
    session_id: LineaID
    ipython: InteractiveShell
    # If passed in, is a Jupyter display handle which should be updated
    # with the new graph SVG after each cell
    visualize_display: DisplayHandle

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

        # Write the code text to a file for error reporting
        get_cell_path(location).write_text(code)

        last_node = transform(code, location, self.tracer)
        if self.visualize_display:
            self.visualize_display.update(SVG(self.tracer.visualize_to_svg()))

        # Return the last value so it will be printed, if we don't end
        # in a semicolon
        ends_with_semicolon = lines and lines[-1].strip().endswith(";")

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


original_get_exc_info = InteractiveShell._get_exc_info


def custom_get_exc_info(*args, **kwargs):
    return transform_except_hook_args(
        # Add an extra frame on top, since ipython will strip out the first
        # one
        original_get_exc_info(*args, **kwargs),
        AddFrame("", 0),
    )
