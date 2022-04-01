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
    Return the path to the temporary file for the given cell.
    This is used for both generating the file and accesssing the file.
    """
    global _temp_dir
    if not _temp_dir:
        _temp_dir = TemporaryDirectory("linea_ipython")

    return (
        Path(_temp_dir.name) / f"{cell.session_id}_{cell.execution_count}.py"
    )


def get_location_path(location: SourceCodeLocation) -> Path:
    """
    Currently, this function is used exclusively for accurate error reporting
    (e.g., when there is an exception, such as `1/0`).
    Without providing a file path, the errors will show up as "?" in both
    IPython and CLI executions.

    We had add the `get_cell_path` as a special case because the file location
    is managed separately by us (not the user provided file path).
    """
    if isinstance(location, JupyterCell):
        return get_cell_path(location)
    return location
