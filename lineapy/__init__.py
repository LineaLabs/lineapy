import atexit

from lineapy.api.api import catalog, get, save, to_pipeline
from lineapy.data.graph import Graph
from lineapy.data.types import SessionType, ValueType
from lineapy.editors.ipython import start, stop, visualize
from lineapy.execution.context import get_context
from lineapy.instrumentation.tracer import Tracer
from lineapy.utils.lineabuiltins import db, file_system

__all__ = [
    "Graph",
    "Tracer",
    "save",
    "get",
    "catalog",
    "to_pipeline",
    "SessionType",
    "ValueType",
    "_is_executing",
    "visualize",
    "db",
    "file_system",
    "__version__",
]

__version__ = "0.0.5"

# Create an ipython extension that starts and stops tracing
# https://ipython.readthedocs.io/en/stable/config/extensions/index.html#writing-extensions
# Can be used like %load_ext lineapy


def load_ipython_extension(ipython):
    atexit.register(stop)
    start(ipython=ipython)


def unload_ipython_extension(ipython):
    stop()


def _is_executing() -> bool:
    try:
        get_context()
    except RuntimeError:
        return False
    return True
