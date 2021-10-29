"""
We write each ipython cell to its own temporary file, so that if an exception is
raised it will have proper tracebacks.

This is how ipython handles it internally as well, so we do the same.
"""


from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

from lineapy.data.types import JupyterCell, SourceCodeLocation

_temp_dir: Optional[TemporaryDirectory] = None


def cleanup_cells():
    """
    Remove the temporary directory with all of the files
    """
    global _temp_dir
    if _temp_dir:
        _temp_dir.cleanup()
        _temp_dir = None


def get_cell_path(cell: JupyterCell) -> Path:
    """
    Return the path to the temporary file for the given cell
    """
    global _temp_dir
    if not _temp_dir:
        _temp_dir = TemporaryDirectory("linea_ipython")

    return (
        Path(_temp_dir.name) / f"{cell.session_id}_{cell.execution_count}.py"
    )


def get_location_path(location: SourceCodeLocation) -> Path:
    if isinstance(location, JupyterCell):
        return get_cell_path(location)
    return location
