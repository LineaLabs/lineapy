import sys
from types import TracebackType
from typing import Optional, Type

from lineapy.exceptions.flag import REWRITE_EXCEPTIONS
from lineapy.exceptions.user_exception import (
    TracebackChange,
    UserException,
    apply_changes,
)

ExceptHookArgs = tuple[Type[Exception], Exception, Optional[TracebackType]]


def transform_except_hook_args(
    args: ExceptHookArgs, *changes: TracebackChange
) -> ExceptHookArgs:
    """
    Pull out the cause from a user exception, and also apply the changes if we
    find it.
    """
    exc_value = args[1]
    if isinstance(exc_value, UserException):
        cause = exc_value.__cause__
        apply_changes(cause, changes)
        return type(cause), cause, cause.__traceback__
    return args


def custom_excepthook(*args):
    """
    Sets an exception hook, so that if an exception is raised, if it's a user
    exception, then the traceback will only be the inner cause, not the outer frames.
    """
    return sys.__excepthook__(*transform_except_hook_args(args))  # type: ignore


def set_custom_excepthook():
    if REWRITE_EXCEPTIONS:
        sys.excepthook = custom_excepthook
