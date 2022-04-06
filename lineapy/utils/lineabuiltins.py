from __future__ import annotations

import sys
from typing import (
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

from lineapy.editors.ipython_cell_storage import get_location_path
from lineapy.instrumentation.annotation_spec import ExternalState
from lineapy.system_tracing.exec_and_record_function_calls import (
    exec_and_record_function_calls,
)

# Keep a list of builtin functions we want to expose to the user as globals
# Then at the end, make a dict out of all of them, from their names


if sys.version_info >= (3, 8):
    from typing import Protocol

    class HasName(Protocol):
        @property
        def __name__(self) -> str:
            ...

else:

    class HasName:
        @property
        def __name__(self) -> str:
            ...


_builtins: List[HasName] = []

if sys.version_info >= (3, 8):

    HAS_NAME = TypeVar("HAS_NAME", bound=HasName)

    def register(b: "HAS_NAME") -> "HAS_NAME":
        _builtins.append(b)
        return b

else:

    def register(b):
        _builtins.append(b)
        return b


@register
def l_list(*items) -> List:
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


@register
def l_dict_kwargs_sentinel() -> _DictKwargsSentinel:
    return _DictKwargsSentinel()


K = TypeVar("K")
V = TypeVar("V")


@register
def l_dict(
    *keys_and_values: Union[
        Tuple[K, V], Tuple[_DictKwargsSentinel, Mapping[K, V]]
    ]
) -> Dict[K, V]:
    """
    Build a dict from a number of key value pairs.

    There is a special case for dictionary unpacking. In this case, the
    key will be an instance of _DictKwargsSentinel.

    For example, if the user creates a dict like ``{1: 2, **d, 3: 4}``,
    then it will create a call like::

        l_dict((1, 2), (l_dict_kwargs_sentinel(), d), (3, 4))

    We use a sentinel value instead of None, because None can be a valid
    dictionary key.
    """
    d: Dict[K, V] = {}
    for (key, value) in keys_and_values:
        if isinstance(key, _DictKwargsSentinel):
            d.update(value)  # type: ignore
        else:
            d[key] = value  # type: ignore
    return d


@register
def l_tuple(*items) -> tuple:
    return items


@register
def l_set(*items) -> set:
    return set(items)


@register
def l_assert(v: object, message: Optional[str] = None) -> None:
    if message is None:
        assert v
    else:
        assert v, message


# Magic variable name used internally in the `__exec__` function, when we
# are execuing an expression and want to save its result. To do so, we have
# to set it to a variable, then retrieve that variable from the scope.
_EXEC_EXPRESSION_SAVED_NAME = "__linea_expresion__"


@register
def l_exec_statement(code: str) -> None:
    """
    Executes code statements. These typically are ast nodes that inherit from ast.stmt.
    Examples include ast.ClassDef, ast.If, ast.For, ast.FunctionDef, ast.While, ast.Try, ast.With

    Execute the `code` with `input_locals` set as locals,
    and returns a list of the `output_locals` pulled from the environment.

    :return: None. Since the code is a statement, it will not return anything
    """
    # Move inside to avoid circular import with context using the lookups to trace
    from lineapy.execution.context import get_context

    context = get_context()
    source_location = context.node.source_location
    if source_location:
        location = source_location.source_code.location
        # Pad the code with extra lines, so that the linenumbers match up
        code = (source_location.lineno - 1) * "\n" + code
        path = str(get_location_path(location))
    else:
        path = "<unkown>"
    bytecode = compile(code, path, "exec")
    trace_fn = exec_and_record_function_calls(
        bytecode, context.global_variables
    )
    # If we were able to understand all the opcode, then save the function calls, otherwise throw them away
    # and depend on the worst case assumptions
    if not trace_fn.not_implemented_ops:
        context.function_calls = trace_fn.function_calls


@register
def l_exec_expr(code: str) -> object:
    """
    Executes code expressions. These typically are ast nodes that inherit from ast.expr.
    Examples include ast.ListComp, ast.Lambda

    Execute the `code` with `input_locals` set as locals,
    and returns a list of the `output_locals` pulled from the environment.

    :return: it will return the result as well as the last argument.

    """
    from lineapy.execution.context import get_context

    context = get_context()

    statement_code = f"{_EXEC_EXPRESSION_SAVED_NAME} = {code}"
    l_exec_statement(statement_code)

    res = context.global_variables[_EXEC_EXPRESSION_SAVED_NAME]
    del context.global_variables[_EXEC_EXPRESSION_SAVED_NAME]

    return res


@register
def l_alias(item: object) -> object:
    return item


T = TypeVar("T")


@register
def l_unpack_sequence(xs: Iterable[T], n: int) -> List[T]:
    """
    Asserts the iterable `xs` is of length `n` and turns it into a list.

    The same as `l_list` but asserts the length. This was modeled after the UNPACK_SEQUENCE
    bytecode to be used in unpacking

    The result should be a view of the input.
    """
    try:
        res = list(xs)
    except TypeError:
        raise TypeError(
            f"cannot unpack non-iterable {type(xs).__name__} object)"
        )
    actual_n = len(res)
    if actual_n > n:
        raise ValueError(f"too many values to unpack (expected {n})")
    if actual_n < n:
        raise ValueError(
            f"not enough values to unpack (expected {n}, got {actual_n})"
        )
    return res


@register
def l_unpack_ex(
    xs: Iterable[T], before: int, after: int
) -> List[Union[T, List[T]]]:
    """
    Slits the iterable `xs` into three pieces and then joins them `[*first, middle, *list]`
    The first of length `before`, the last of length `after`, and the middle whatever is remaining.

    Modeled after the UNPACK_EX bytecode to be used in unpacking.
    """
    try:
        xs_list = list(xs)
    except TypeError:
        raise TypeError(
            f"cannot unpack non-iterable {type(xs).__name__} object)"
        )
    xs_n = len(xs_list)
    min_values = before + after
    if xs_n < min_values:
        raise ValueError(
            f"not enough values to unpack (expected at least {min_values}, got {xs_n})"
        )
    before_list = xs_list[:before]
    if after != 0:
        after_list = xs_list[-after:]
        middle_list = xs_list[before:-after]
    else:
        after_list = []
        middle_list = xs_list[before:]
    return [*before_list, middle_list, *after_list]


file_system = register(ExternalState(external_state="file_system"))
db = register(ExternalState(external_state="db"))


LINEA_BUILTINS = {f.__name__: f for f in _builtins}
