import os

from lineapy.api import catalog, get, save
from lineapy.constants import ExecutionMode
from lineapy.data.graph import Graph
from lineapy.data.types import SessionType, ValueType
from lineapy.instrumentation.tracer import Tracer
from lineapy.ipython import start, stop

__all__ = [
    "Graph",
    "Tracer",
    "save",
    "get",
    "catalog",
    "SessionType",
    "ExecutionMode",
    "ValueType",
    "__version__",
]

__version__ = "0.0.1"

# Create an ipython extension that starts and stops tracing
# https://ipython.readthedocs.io/en/stable/config/extensions/index.html#writing-extensions
# Can be used like %load_ext lineapy


def load_ipython_extension(ipython):
    ipython.set_hook("shutdown_hook", unload_ipython_extension)

    start(ipython=ipython)


def unload_ipython_extension(ipython):
    stop(
        ipython=ipython,
        visualization_filename=os.environ.get(
            "LINEA_VISUALIZATION_NAME", None
        ),
    )
