import sys
from typing import Any, Callable, Iterable, Optional, Set, Tuple, TypeVar, cast
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


"""
Type checking utils
"""


def get_literal_value_from_string(
    val: str, literal_type: LiteralType
) -> object:
    if literal_type == LiteralType.Integer:
        return int(val)
    if literal_type == LiteralType.Float:
        return float(val)
    if literal_type == LiteralType.Boolean:
        return val == "True"
    if literal_type == LiteralType.NoneType:
        return None
    if literal_type == LiteralType.String:
        return val
    if literal_type == LiteralType.Ellipsis:
        return ...
    raise NotImplementedError(f"Unsupported literal type: {literal_type}")


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
    if isinstance(val, (list, str, int)):
        return ValueType.array
    if "pandas" in sys.modules:
        import pandas  # this import should be a no-op

        if isinstance(val, pandas.core.frame.DataFrame):
            return ValueType.dataset  # FIXME
        if isinstance(val, pandas.core.series.Series):
            return ValueType.dataset  # FIXME

    if "PIL" in sys.modules:
        import PIL

        if hasattr(PIL, "PngImagePlugin"):
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


CALLABLE = TypeVar("CALLABLE", bound=Callable)


def listify(fn: CALLABLE) -> CALLABLE:
    """
    TODO: Once we switch to Python 3.10, we can type this properly
    https://www.python.org/dev/peps/pep-0612/
    """

    def wrapper(*args, **kwargs):
        return list(fn(*args, **kwargs))

    return cast(CALLABLE, wrapper)


# These are some helper functions we need since we are using lists as ordered
# sets.

T = TypeVar("T")


def remove_duplicates(xs: Iterable[T]) -> Iterable[T]:
    """
    Remove all duplicate items, maintaining order.
    """
    seen_: Set[int] = set()
    for x in xs:
        h = hash(x)
        if h in seen_:
            continue
        seen_.add(h)
        yield x


def remove_value(xs: Iterable[T], x: T) -> Iterable[T]:
    """
    Remove all items equal to x.
    """
    for y in xs:
        if x != y:
            yield y


def get_lib_package_version(name: str) -> Tuple[str, str]:
    mod = sys.modules[name]
    package_name = mod.__name__
    mod_version: Any = None
    if hasattr(mod, "__version__"):
        mod_version = mod.__version__
    else:
        # package is probably a submodule
        parent_package_name = name.split(".")[0]
        parent_package = sys.modules[parent_package_name]
        package_name = parent_package.__name__
        if hasattr(parent_package, "__version__"):
            mod_version = parent_package.__version__
    return package_name if package_name else name, str(mod_version)
