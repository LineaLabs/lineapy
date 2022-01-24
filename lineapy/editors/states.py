from dataclasses import dataclass, field
from typing import Optional

from IPython.core.interactiveshell import InteractiveShell
from IPython.display import DisplayHandle


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
    # tracer: Tracer
    # The code for this cell's execution
    code: str
    # If set, we should update this display on every cell execution.
    visualize_display_handle: Optional[DisplayHandle] = field(default=None)

    # This is set to true, if `stop()` is called in the cell
    # to signal that at the end of this cell we should stop tracing.
    # We don't stop immediately, so we can return the proper value from the cell
    should_stop: bool = field(default=False)
