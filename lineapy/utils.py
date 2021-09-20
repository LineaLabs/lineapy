import sys
from typing import Any, Optional
from uuid import uuid4
from time import time

from lineapy.data.types import (
    LiteralType,
    ValueType,
)


"""
Error logging utils
"""


class bcolors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    GREY = "\033[37m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class InternalLogicError(Exception):
    def __init__(self, message):
        super().__init__(message)


class FunctionShouldNotBeCalled(Exception):
    def __init__(self, message):
        super().__init__(message)


class WrongTypeError(Exception):
    def __init__(self, message):
        super().__init__(message)


class CaseNotHandledError(Exception):
    def __init__(self, message):
        super().__init__(message)


class UserError(Exception):
    def __init__(self, message):
        super().__init__(message)


class NullValueError(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidStateError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ValueNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)


def check_not_null(val: Any, err_msg: Optional[str] = None):
    if val is None:
        raise NullValueError(err_msg)


def type_check_with_warning(val: Any, t: Any):
    if not (isinstance(val, t)):
        err_msg = f"expected variable to be {t} but got {val} instead"
        raise WrongTypeError(err_msg)


def report_error_to_user(msg: str):
    print(bcolors.WARNING + "[Warning] " + msg + bcolors.ENDC)


def internal_warning_log(*args):
    print(bcolors.WARNING + "🔥", *args, "🔥", bcolors.ENDC)


def info_log(*args):
    if IS_DEBUG:
        print(bcolors.GREEN + "[Info] ", *args, "\n" + bcolors.ENDC)


def debug_log(msg: str):
    if IS_DEBUG:
        print(bcolors.WARNING + msg + bcolors.ENDC)


"""
Data gen utils
"""


def get_new_id() -> str:
    # https://docs.python.org/3/library/uuid.html#module-uuid seems to use str
    #   instead of hex, so that's why
    return str(uuid4())


def get_current_time():
    return time()


IS_DEBUG = True


"""
Type checking utils
"""


def is_integer(val):
    try:
        int(val)
    except Exception:
        return False
    return True


def get_literal_value_from_string(val: str, literal_type: LiteralType) -> Any:
    if literal_type is LiteralType.Integer:
        return int(val)
    elif literal_type is LiteralType.Boolean:
        return val == "True"
    return val


def jsonify_value(value: Any, value_type: ValueType) -> str:
    if value_type == ValueType.dataset:
        return value.to_csv(index=False)
    if value_type == ValueType.value:
        return str(value)

    raise CaseNotHandledError(
        f"Was not able to jsonify value of type {value_type}"
    )


def get_value_type(val: Any) -> ValueType:
    """
    Got a little hacky so as to avoid dependency on external libraries.
    Current method is to check if the dependent library is already imported,
      if they are, then we can reference them.

    Note:
    - Watch out for error here if the Executor tests fail.
    TODO
    - We need to more gracefully handle cases that we do not recognize
    """
    if is_integer(val):
        return ValueType.value
    if isinstance(val, str):
        return ValueType.value
    if isinstance(val, list):
        return ValueType.array
    if "matplotlib" in sys.modules:
        from matplotlib.figure import Figure

        if isinstance(val, Figure):
            raise NotImplementedError(
                "We have yet to support dealing with matplotlib figs."
            )
    if "numpy" in sys.modules:
        import numpy

        if isinstance(val, numpy.ndarray):
            raise NotImplementedError("We have yet to support numpy arrays.")
    if "pandas" in sys.modules:
        import pandas  # this import should be a no-op

        if isinstance(val, pandas.core.frame.DataFrame):
            return ValueType.dataset  # FIXME
        if isinstance(val, pandas.core.series.Series):
            return ValueType.dataset  # FIXME

    if "PIL" in sys.modules:
        import PIL

        if isinstance(val, PIL.PngImagePlugin.PngImageFile):
            return ValueType.chart
        if isinstance(val, PIL.Image.Image):
            return ValueType.chart

    raise CaseNotHandledError(
        f"Do not know the type of {val}, type {type(val)}"
    )
