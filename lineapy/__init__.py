from lineapy.constants import ExecutionMode
from lineapy.data.graph import Graph
from lineapy.data.types import SessionType
from lineapy.instrumentation.tracer import Tracer
from lineapy.utils import FunctionShouldNotBeCalled

__version__ = "0.0.1"

from typing import Any, Optional


def linea_publish(variable: Any, description: Optional[str] = None) -> None:
    """
    Publishes artifact to the linea repo
    """
    """
    DEV NOTEs:
    - If you are going to change he name of this function, it must match the
      constant `LINEAPY_PUBLISH_FUNCTION_NAME` in `constants.py`.
    - This method is instrumented by transformer to be called by the tracer
    """

    raise FunctionShouldNotBeCalled(
        """This method must be used along with a custom Linea Kernel,
          or the Linea Cli."""
    )


def publish_with_tracer(
    variable_name: str, description: Optional[str], tracer: Tracer
) -> None:
    tracer.publish(variable_name, description)


__all__ = [
    "Graph",
    "Tracer",
    "linea_publish",
    "publish_with_tracer",
    "SessionType",
    "ExecutionMode",
    "__version__",
]
