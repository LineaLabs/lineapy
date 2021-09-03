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


def get_execution_mode_str(m: ExecutionMode):
    """
    Note:
    - this is pretty tedious
    - looked into maybe using strings but this post makes me think it's not possible? https://stackoverflow.com/questions/43862184/associating-string-representations-with-an-enum-that-uses-integer-values
    """
    if m == ExecutionMode.TEST:
        return "TEST"
    if m == ExecutionMode.DEV:
        return "DEV"
    if m == ExecutionMode.PROD:
        return "PROD"
