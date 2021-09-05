from enum import Enum

LINEAPY_TRACER_CLASS = "Tracer"
LINEAPY_TRACER_NAME = "lineapy_tracer"
LINEAPY_IMPORT_LIB_NAME = "lineapy"
LINEAPY_SESSION_TYPE = "SessionType"
LINEAPY_SESSION_TYPE_JUPYTER = "JUPYTER"
LINEAPY_SESSION_TYPE_SCRIPT = "SCRIPT"
LINEAPY_EXECUTION_MODE = "ExecutionMode"


class ExecutionMode(Enum):
    """
    This is not a constant because this is for runtime configuration
    """

    TEST = 0
    DEV = 1
    PROD = 2
