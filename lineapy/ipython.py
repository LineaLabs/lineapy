"""
Code to transform inputs when running in IPython, to trace them.
"""
from typing import Optional
from lineapy.constants import ExecutionMode


def trace(session_name: Optional[str]=None, mode: ExecutionMode = ExecutionMode.MEMORY) -> None:
    """
    Trace any subsequent cells with linea.
    """
    pass

def stop() -> None:
    """
    Stop tracing.
    """
    pass