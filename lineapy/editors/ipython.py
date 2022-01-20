"""
Transforms all executions in IPython to execute with lineapy, by
adding to input_transformers_post.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union

from IPython.core.interactiveshell import InteractiveShell
from IPython.display import DisplayHandle, DisplayObject, display

from lineapy.data.types import JupyterCell, SessionType
from lineapy.db.db import RelationalLineaDB
from lineapy.editors.ipython_cell_storage import cleanup_cells, get_cell_path
from lineapy.exceptions.excepthook import transform_except_hook_args
from lineapy.exceptions.flag import REWRITE_EXCEPTIONS
from lineapy.exceptions.user_exception import AddFrame
from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.node_transformer import transform
from lineapy.utils.logging_config import configure_logging

__all__ = ["_end_cell", "start", "stop", "visualize"]

# The state of the ipython extension works like:
# 1. Originally starts at `None``, meaning that no ipython transformations are active
# 2. After calling `start`, it transitions to `Started`, which means that the
#    the transformer is registered and the exceptions will be transformed.
# 3. After the first cell is executed, the state changes to `CellsExecuted`,
#    which means we have connected to the database and have started saving traces.
#    Note: We wait to connect to the DB till the first cell is executed, so that
#    any logging printed during this connection, or errors raised during this connection
#    are displayed to users, instead of being lost, if the start is called during
#    an extension load during ipython startup.
# SS: do not explicitly set the state to `None` here
STATE: Union[None, StartedState, CellsExecutedState]


@dataclass
class StartedState:
    # Save the ipython in the started state, because we can't look it
    # up during our transformation, and we need it to get the globals
    ipython: InteractiveShell

    # Optionally overrides for the session name and DB URL
    session_name: Optional[str]
    db_url: Optional[str]


@dataclass
class CellsExecutedState:
    tracer: Tracer
    # The code for this cell's execution
    code: str
    # If set, we should update this display on every cell execution.
    visualize_display_handle: Optional[DisplayHandle] = field(default=None)

    # This is set to true, if `stop()` is called in the cell
    # to signal that at the end of this cell we should stop tracing.
    # We don't stop immediately, so we can return the proper value from the cell
    should_stop: bool = field(default=False)

    def create_visualize_display_object(self) -> DisplayObject:
        """
        Returns a jupyter display object for the visualization.
        """
        from lineapy.visualizer import Visualizer

        return Visualizer.for_public(self.tracer).ipython_display_object()


def start(
    session_name: Optional[str] = None,
    db_url: Optional[str] = None,
    ipython: Optional[InteractiveShell] = None,
) -> None:
    """
    Trace any subsequent cells with linea.
    """
    global STATE
    ipython = ipython or get_ipython()  # type: ignore
    # Ipython does not use exceptionhook, so instead we monkeypatch
    # how it processes the exceptions, in order to add our handler
    # that removes the outer frames.
    if REWRITE_EXCEPTIONS:
        InteractiveShell._get_exc_info = custom_get_exc_info

    ipython.input_transformers_post.append(input_transformer_post)
    STATE = StartedState(ipython, session_name=session_name, db_url=db_url)


def input_transformer_post(lines: List[str]) -> List[str]:
    """
    Translate the lines of code for the cell provided by ipython.
    """
    global STATE
    if not STATE:
        raise RuntimeError(
            "input_transformer_post shouldn't be called when we don't have an active tracer"
        )
    code = "".join(lines)
    # If we have just started, first start everything up
    if isinstance(STATE, StartedState):
        # Configure logging so that we the linea db prints it has connected.
        configure_logging("INFO")
        db = RelationalLineaDB.from_environment(STATE.db_url)
        # pass in globals from ipython so that `get_ipthon()` works
        # and things like `!cat df.csv` work in the notebook
        ipython_globals = STATE.ipython.user_global_ns
        tracer = Tracer(
            db, SessionType.JUPYTER, STATE.session_name, ipython_globals
        )

        STATE = CellsExecutedState(tracer, code=code)
    else:
        STATE.code = code

    return RETURNED_LINES


# We always return the same two lines for IPython to use as input.
# They will run our internal end cell function, which wil return the proper
# return value for the cell, so ipython can display it. They will also clean
# up the tracer if we stopped in that cell.
RETURNED_LINES = [
    "import lineapy.editors.ipython\n",
    "lineapy.editors.ipython._end_cell()\n",
]


def _end_cell() -> object:
    """
    Returns the last value that was executed, used when rendering the cell,
    and also stops the tracer if we asked it to stop in the cell.
    """
    global STATE
    if not isinstance(STATE, CellsExecutedState):
        raise ValueError("We need to be executing cells to get the last value")

    execution_count: int = get_ipython().execution_count  # type: ignore
    location = JupyterCell(
        execution_count=execution_count,
        session_id=STATE.tracer.session_context.id,
    )
    code = STATE.code
    # Write the code text to a file for error reporting
    get_cell_path(location).write_text(code)

    last_node = transform(code, location, STATE.tracer)
    if STATE.visualize_display_handle:
        STATE.visualize_display_handle.update(
            STATE.create_visualize_display_object()
        )

    # Return the last value so it will be printed, if we don't end
    # in a semicolon
    ends_with_semicolon = code.strip().endswith(";")
    if not ends_with_semicolon and last_node:
        res = STATE.tracer.executor.get_value(last_node)
    else:
        res = None
    _optionally_stop(STATE)
    return res


def visualize(*, live=False) -> None:
    """
    Display a visualization of the Linea graph from this session using Graphviz.

    If `live=True`, then this visualization will live update after cell execution.
    Note that this comes with a substantial performance penalty, so it is False
    by default.

    Note: If the visualization is not live, it will print out the visualization
    as of the previous cell execution, not the one where `visualize` is executed.
    """
    if not isinstance(STATE, CellsExecutedState):
        raise RuntimeError(
            "Cannot visualize before we have started executing cells"
        )
    display_object = STATE.create_visualize_display_object()
    if live:
        # If we have an existing display handle, display a new version of it.
        if STATE.visualize_display_handle:
            STATE.visualize_display_handle.display(display_object)
        # Otherwise, create a new one
        else:
            STATE.visualize_display_handle = display(
                display_object, display_id=True
            )
    else:
        # Otherwise, just display the visualization
        display(display_object)


def stop() -> None:
    """
    Tell the tracer to stop after this cell
    """
    global STATE

    if not STATE:
        return

    if not isinstance(STATE, CellsExecutedState):
        raise RuntimeError("Cannot stop executing if we haven't started yet.")
    STATE.should_stop = True


def _optionally_stop(cells_executed_state: CellsExecutedState) -> None:
    """
    Stop tracing if the `stop()` was called in the cell and should_stop was set.
    """
    global STATE

    # If stop was triggered during in this cell, clean up
    if not cells_executed_state.should_stop:
        return
    STATE = None
    ipython: InteractiveShell = get_ipython()  # type: ignore
    ipython.input_transformers_post.remove(input_transformer_post)
    cells_executed_state.tracer.db.close()
    # Remove the cells we stored
    cleanup_cells()
    # Reset the exception handling
    InteractiveShell._get_exc_info = original_get_exc_info


# Save the original get_exc_info so that we can call it in our custom one
# after transforming
original_get_exc_info = InteractiveShell._get_exc_info


def custom_get_exc_info(*args, **kwargs):
    """
    A custom get_exc_info which will transform exceptions raised from the users
    code to remove our frames that we have added.
    """
    return transform_except_hook_args(
        original_get_exc_info(*args, **kwargs),
        # Add an extra frame on top, since ipython will strip out the first
        # one
        AddFrame("", 0),
    )
