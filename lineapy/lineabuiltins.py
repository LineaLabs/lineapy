from dataclasses import dataclass
from typing import Callable, List, Mapping, Optional, TypeVar, Union

from lineapy.data.types import CallNode, SourceLocation
from lineapy.ipython_cell_storage import get_location_path

# Keep a list of builtin functions we want to expose to the user as globals
_builtin_functions: list[Callable] = []


def l_list(*items) -> List:
    return list(items)


_builtin_functions.append(l_list)


class _DictKwargsSentinel(object):
    """
    A sentinel object to be passed into __build_dict__ to signal that a certain
    args is passed in as kwargs.
    There is currently a PEP for a standard Python sentinel:
    https://www.python.org/dev/peps/pep-0661/#id16
    We use a custom class currently to aid in the typing.
    """

    pass


def l_dict_kwargs_sentinel() -> _DictKwargsSentinel:
    return _DictKwargsSentinel()


_builtin_functions.append(l_dict_kwargs_sentinel)


K = TypeVar("K")
V = TypeVar("V")


def l_dict(
    *keys_and_values: Union[
        tuple[K, V], tuple[_DictKwargsSentinel, Mapping[K, V]]
    ]
) -> dict[K, V]:
    """
    Build a dict from a number of key value pairs.

    There is a special case for dictionary unpacking. In this case, the
    key will be an instance of _DictKwargsSentinel.

    For example, if the user creates a dict like {1: 2, **d, 3: 4},
    then it will create a call like"
    __build_dict__((1, 2), (__build_dict_kwargs_sentinel__(), d), (3, 4))

    We use a sentinel value instead of None, because None can be a valid
    dictionary key.
    """
    d: dict[K, V] = {}
    for (key, value) in keys_and_values:
        if isinstance(key, _DictKwargsSentinel):
            d.update(value)  # type: ignore
        else:
            d[key] = value  # type: ignore
    return d


_builtin_functions.append(l_dict)


def l_tuple(*items) -> tuple:
    return items


_builtin_functions.append(l_tuple)


def l_assert(v: object, message: Optional[str] = None) -> None:
    if message is None:
        assert v
    else:
        assert v, message


_builtin_functions.append(l_assert)


# Magic variable name used internally in the `__exec__` function, when we
# are execuing an expression and want to save its result. To do so, we have
# to set it to a variable, then retrieve that variable from the scope.
_EXEC_EXPRESSION_SAVED_NAME = "__linea_expresion__"


class RecordGetitemDict(dict):
    """
    A custom dict that records which keys have been succesfully accessed.

    We cannot overload the `__setitem__` method, since Python will not respect
    it for custom globals, but we can overload the __getitem__ method.

    See https://stackoverflow.com/a/12185315/907060
    which refers to https://bugs.python.org/issue14385
    """

    def __init__(self, *args, **kwargs):
        self._getitems: list[str] = []
        super().__init__(*args, **kwargs)

    def __getitem__(self, k):
        r = super().__getitem__(k)
        if k not in self._getitems:
            self._getitems.append(k)
        return r


# Before executing, we save the current source location, in this global,
# So we can compile code with the proper traceback, by using the filename
# and line number.
CURRENT_SOURCE_LOCATION: Optional[SourceLocation] = None

# We use the same globals dict for all exec calls, so that we can set our scope
# variables for any functions that are defined in the exec
_exec_globals = RecordGetitemDict()


def l_exec_statement(code: str) -> None:
    """
    Execute the `code` with `input_locals` set as locals,
    and returns a list of the `output_locals` pulled from the environment.

    If the code is an expression, it will return the result as well as the last
    argument.
    """
    if CURRENT_SOURCE_LOCATION:
        location = CURRENT_SOURCE_LOCATION.source_code.location
        # Pad the code with extra lines, so that the linenumbers match up
        code = (CURRENT_SOURCE_LOCATION.lineno - 1) * "\n" + code
        path = str(get_location_path(location))
    else:
        path = "<unkown>"
    bytecode = compile(code, path, "exec")
    exec(bytecode, _exec_globals)


_builtin_functions.append(l_exec_statement)


def l_exec_expr(code: str) -> object:
    """
    Execute the `code` with `input_locals` set as locals,
    and returns a list of the `output_locals` pulled from the environment.

    If the code is an expression, it will return the result as well as the last
    argument.
    """
    statement_code = f"{_EXEC_EXPRESSION_SAVED_NAME} = {code}"
    l_exec_statement(statement_code)

    res = _exec_globals[_EXEC_EXPRESSION_SAVED_NAME]
    del _exec_globals[_EXEC_EXPRESSION_SAVED_NAME]

    return res


_builtin_functions.append(l_exec_expr)


@dataclass(frozen=True)
class FileSystem:
    def make_node(self) -> CallNode:
        return CallNode(
            name="make_node",
            args=[],
            kwargs={},
            source_location=CURRENT_SOURCE_LOCATION,
        )


LINEA_BUILTINS = {f.__name__: f for f in _builtin_functions}
