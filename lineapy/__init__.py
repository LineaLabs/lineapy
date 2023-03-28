import atexit

from lineapy.api.api import (
    LineaArtifact,
    Pipeline,
    artifact_store,
    create_pipeline,
    delete,
    get,
    get_function,
    get_module,
    get_module_definition,
    get_pipeline,
    reload,
    save,
    to_pipeline,
)
from lineapy.data.graph import Graph
from lineapy.data.types import SessionType, ValueType
from lineapy.editors.ipython import start, stop, visualize
from lineapy.execution.context import get_context
from lineapy.instrumentation.tracer import Tracer
from lineapy.utils.analytics.usage_tracking import tag
from lineapy.utils.config import options
from lineapy.utils.lineabuiltins import db, file_system
from lineapy.utils.version import __version__

__all__ = [
    "Graph",
    "Tracer",
    "save",
    "get",
    "get_pipeline",
    "get_function",
    "get_module",
    "get_module_definition",
    "artifact_store",
    "delete",
    "reload",
    "to_pipeline",
    "create_pipeline",
    "SessionType",
    "ValueType",
    "_is_executing",
    "visualize",
    "db",
    "file_system",
    "options",
    "tag",
    "__version__",
    "LineaArtifact",
    "Pipeline",
]


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
