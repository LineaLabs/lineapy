from typing import Any, Optional


def linea_publish(variable: Any, description: Optional[str] = None) -> None:
    """
    Publishes artifact to the linea repo
    """
    """
    DEV NOTEs:
    - This method is instrumented by transformer to be called by the tracer
    """

    raise RuntimeError(
        """This method must be used along with a custom Linea Kernel,
          or the Linea Cli."""
    )
