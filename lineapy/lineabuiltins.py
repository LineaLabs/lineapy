# Keep unused import for transitive import by Executor
from operator import *
from types import FunctionType  # noqa: F403,F401
from typing import List, Mapping, Optional, TypeVar, Union

# NOTE: previous attempt at some import issues with the operator model
#   from operator import *


def __build_list__(*items) -> List:
    return list(items)


class _DictKwargsSentinel(object):
    """
    A sentinel object to be passed into __build_dict__ to signal that a certain
    args is passed in as kwargs.
    There is currently a PEP for a standard Python sentinel:
    https://www.python.org/dev/peps/pep-0661/#id16
    We use a custom class currently to aid in the typing.
    """

    pass


class _VariableNotSetSentinel(object):
    """
    A sentinel object to let us know that an object is not set at runtime
      this is useful when we do static analysis and do not know which
      branch was executed, e.g. in
      ```
      if True:
        c = 10
        if True:
          k = 6
      else:
        d = 5
      ```
      `c` and `k` will be set, but `d` will NOT be!

    """

    pass


def __build_dict_kwargs_sentinel__() -> _DictKwargsSentinel:
    return _DictKwargsSentinel()


K = TypeVar("K")
V = TypeVar("V")


def __build_dict__(
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


def __build_tuple__(*items) -> tuple:
    return items


def __assert__(v: object, message: Optional[str] = None) -> None:
    if message is None:
        assert v
    else:
        assert v, message


# Magic variable name used internally in the `__exec__` function, when we
# are execuing an expression and want to save its result. To do so, we have
# to set it to a variable, then retrieve that variable from the scope.
_EXEC_EXPRESSION_SAVED_NAME = "__linea_expresion__"


# We use the same globals dict for all exec calls, so that we can set our scope
# variables for any functions that are defined in the exec
_exec_globals = {}


def set_exec_globals(globals_: dict[str, object]) -> None:
    """
    Set the global environment for the `__exec__` function.
    """
    _exec_globals.update(globals_)


def clear_exec_globals() -> None:
    _exec_globals.clear()


def function_defined_in_exec(fn: FunctionType) -> bool:
    return fn.__globals__ is _exec_globals


def __exec__(
    code: str, is_expr: bool, *output_locals: str, **input_locals: object
) -> list[Union[object, _VariableNotSetSentinel]]:
    """
    Execute the `code` with `input_locals` set as locals,
    and returns a list of the `output_locals` pulled from the environment.

    If the code is an expression, it will return the result as well as the last
    argument.
    """
    if is_expr:
        code = f"{_EXEC_EXPRESSION_SAVED_NAME} = {code}"
    bytecode = compile(code, "<string>", "exec")
    # Only pass in "globals" so that globals and locals are equivalent,
    # which is the case when executing at the module level, and not at the
    # class body level, see https://docs.python.org/3/library/functions.html#exec
    set_exec_globals(input_locals)
    exec(bytecode, _exec_globals)

    # Iterate through the ouputs we should get back, and look them up in the
    # globals/locals. If they do not exist, return the _VariableNotSetSentinel
    # to represent that that variable was not set. This is used for execing
    # code which could possibly set a variable, but might not, like in an if
    # statement branch
    returned_locals = [
        _exec_globals.get(name, _VariableNotSetSentinel())
        for name in output_locals
    ]
    if is_expr:
        returned_locals.append(_exec_globals[_EXEC_EXPRESSION_SAVED_NAME])

    clear_exec_globals()

    return returned_locals
