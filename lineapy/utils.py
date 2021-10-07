import sys
from time import time
from typing import Any, Callable, Optional, TypeVar, cast
from uuid import uuid4

import black

from lineapy.data.types import LineaID, LiteralType, ValueType

"""
Data gen utils
"""


def get_new_id() -> LineaID:
    # https://docs.python.org/3/library/uuid.html#module-uuid seems to use str
    #   instead of hex, so that's why
    return LineaID(str(uuid4()))


def get_current_time():
    return time()


"""
Type checking utils
"""


def is_integer(val):
    try:
        int(val)
    except Exception:
        return False
    return True


def get_literal_value_from_string(
    val: str, literal_type: Optional[LiteralType]
) -> Any:
    if literal_type is LiteralType.Integer:
        try:
            return int(val)
        except ValueError:
            return float(val)
    elif literal_type is LiteralType.Boolean:
        return val == "True"
    return val


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

    return cast(T, wrapper)
