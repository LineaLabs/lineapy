import sys
from typing import Any, Callable, Optional, TypeVar
from uuid import uuid4
from time import time

import black

from lineapy.data.types import (
    LineaID,
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


def debug_log(*args):
    if IS_DEBUG:
        print(bcolors.WARNING, *args, bcolors.ENDC)


"""
Data gen utils
"""


def get_new_id() -> LineaID:
    # https://docs.python.org/3/library/uuid.html#module-uuid seems to use str
    #   instead of hex, so that's why
    return str(uuid4())


def get_current_time():
    return time()


IS_DEBUG = True


def set_debug(is_debug: bool):
    global IS_DEBUG
    IS_DEBUG = is_debug


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


def get_value_type(val: Any) -> Optional[ValueType]:
    """
    Got a little hacky so as to avoid dependency on external libraries.
    Current method is to check if the dependent library is already imported,
      if they are, then we can reference them.

    Note:
    - Watch out for error here if the Executor tests fail.
    TODO
    - We currently just silently ignore cases we cant handle
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

    return None


def prettify(code: str) -> str:

    return black.format_str(
        code,
        mode=black.Mode(),
    )


T = TypeVar("T", bound=Callable)


def listify(fn: T) -> T:
    """
    TODO: Once we switch to Python 3.10, we can type this properly
    https://www.python.org/dev/peps/pep-0612/
    """

    def wrapper(*args, **kwargs):
        return list(fn(*args, **kwargs))

    return wrapper
