from typing import List, Optional
from operator import *  # Keep unused import for transitive import by Executor

# NOTE: previous attempt at some import issues with the operator model
#   from operator import *


def __build_list__(*items) -> List:
    return list(items)


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
_EXPRESSION_SAVED_NAME = "__linea_expresion__"


def __exec__(
    code: str, is_expr: bool, *output_locals: str, **input_locals: object
) -> list[object]:
    """
    Execute the `code` with `input_locals` set as locals,
    and returns a list of the `output_locals` pulled from the environment.

    If the code is an expression, it will return the result as well as the last
    argument.
    """
    if is_expr:
        code = f"{_EXPRESSION_SAVED_NAME} = {code}"
    bytecode = compile(code, "<string>", "exec")
    exec(bytecode, globals(), input_locals)
    returned_locals = [input_locals[name] for name in output_locals]
    if is_expr:
        returned_locals.append(input_locals[_EXPRESSION_SAVED_NAME])
    return returned_locals
