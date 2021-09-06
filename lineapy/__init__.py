from lineapy.constants import ExecutionMode
from lineapy.data.graph import Graph
from lineapy.data.types import SessionType
from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.constants import ExecutionMode
from lineapy.utils import FunctionShouldNotBeCalled

__version__ = "0.0.1"

from typing import Optional


def publish(variable_name: str, description: Optional[str]) -> None:
    """
    Publishes artifact, notifies the user through printing, and this would be compatible with either scriptingor the notebook: again
    TODO
    - [] Note that we need to instrument this at runtime to pass in the tracer and change the function call
    """

    raise FunctionShouldNotBeCalled("`publish` should have been re-written")


def publish_with_tracer(
    variable_name: str, description: Optional[str], tracer: Tracer
) -> None:
    tracer.publish(variable_name, description)


__all__ = [
    "Graph",
    "Tracer",
    "publish",
    "publish_with_tracer",
    "SessionType",
    "ExecutionMode",
    "__version__",
]
