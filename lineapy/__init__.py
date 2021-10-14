from typing import Any, Optional

from lineapy.constants import ExecutionMode
from lineapy.data.graph import Graph
from lineapy.data.types import SessionType, ValueType
from lineapy.graph_reader.apis import LineaArtifact
from lineapy.instrumentation.tracer import Tracer

__version__ = "0.0.1"

"""
User exposed APIs.

We should keep these external APIs as small as possible, and unless there is
  a very compelling use case, not support more than one way to access the
  same feature.
"""


def save(variable: Any, description: Optional[str] = None) -> None:
    """
    Publishes artifact to the linea repo
    """
    """
    DEV NOTEs:
    - This method is instrumented by transformer to be called by the tracer
    """

    raise RuntimeError(
        """This method should be intrusmented and not invoked."""
    )

def get(artifact_name: str) -> LineaArtifact:
    """
    """
    raise RuntimeError(
        """This method should be intrusmented and not invoked."""
    )

def catalog()

__all__ = [
    "Graph",
    "Tracer",
    "save",
    "SessionType",
    "ExecutionMode",
    "ValueType",
    "__version__",
]
