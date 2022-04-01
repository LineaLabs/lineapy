import sys
from types import TracebackType
from typing import Optional, Tuple, Type

from lineapy.exceptions.flag import REWRITE_EXCEPTIONS
from lineapy.exceptions.user_exception import (
    TracebackChange,
    UserException,
    apply_changes,
)

ExceptHookArgs = Tuple[Type[Exception], Exception, Optional[TracebackType]]


def transform_except_hook_args(
    args: ExceptHookArgs, *changes: TracebackChange
) -> ExceptHookArgs:
    """
    Used by both CLI and Jupyter to pull out the cause from a user exception
    and also apply the changes to the frames if it's a `UserException`, which
    is a custom exception that WE created.

    `changes` is for Jupyter notebook support. They were discovered through trial and error with different type
    of executions, as seen in `executor.py`.

    If the error is from lineapy, we keep the original frames.
    """
    # the 2nd arg is the Exception (per the docs, and described in
    # `ExceptHookArgs`)
    exc_value = args[1]
    if isinstance(exc_value, UserException):
        # the user's exception
        cause = exc_value.__cause__
        apply_changes(cause, changes)
        return type(cause), cause, cause.__traceback__
    return args


def custom_excepthook(*args):
    """
    CLI support.
    Sets an exception hook, so that if an exception is raised, if it's a user
    exception, then the traceback will only be the inner cause, not the outer frames.
    """
    return sys.__excepthook__(*transform_except_hook_args(args))  # type: ignore


def set_custom_excepthook():
    """
    To support CLI error reporting (or the repl, which we do not currently have).
    """
    if REWRITE_EXCEPTIONS:
        sys.excepthook = custom_excepthook
