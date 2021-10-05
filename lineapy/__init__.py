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
    - This method is instrumented by transformer to be called by the tracer
    """

    raise FunctionShouldNotBeCalled(
        """This method must be used along with a custom Linea Kernel,
          or the Linea Cli."""
    )


__all__ = [
    "Graph",
    "Tracer",
    "linea_publish",
    "SessionType",
    "ExecutionMode",
    "__version__",
]


def load_ipython_extension(ipython: Any) -> None:
    """
    When running `%load_ext lineapy` this function
    will be run.
    See https://ipython.readthedocs.io/en/stable/config/custommagics.html#defining-custom-magics
    for information on the `load_ipython_extension` function.
    """
    # Register a custom AST transformation
    # https://ipython.readthedocs.io/en/stable/config/inputtransforms.html#ast-transformations
    Tracer(session_type, session_name, execution_mode)
    ipython.shell.ast_transformers.append(Tracer())
