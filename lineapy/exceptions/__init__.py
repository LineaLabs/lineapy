import sys
from types import TracebackType
from typing import Optional

from lineapy.exceptions.create_frame import create_frame

__all__ = ["UserException", "set_custom_excepthook"]


class UserException(Exception):
    def __init__(
        self,
        cause: Exception,
        *,
        skip_frames: int = 0,
        add_frame: Optional[tuple[str, int]] = None,
    ):

        tb = cause.__traceback__
        # Modify the cause to skip a number of frames
        for _ in range(skip_frames):
            assert tb
            tb = tb.tb_next

        # If adding a frame, create that and the rest as next frames
        if add_frame:
            filename, lineno = add_frame
            code = compile("", filename, "exec")
            tb = TracebackType(
                tb,
                create_frame(code),
                0,
                lineno,
            )
        cause.__traceback__ = tb
        self.__cause__ = cause


def custom_excepthook(exc_type, exc_value, traceback):
    """
    Sets an exception hook, so that if an exception is raised, if it's a user
    exception, then the traceback will only be the inner cause, not the outer frames.
    """
    if exc_type == UserException:
        cause = exc_value.__cause__
        sys.__excepthook__(UserException, cause, cause.__traceback__)
    else:
        sys.__excepthook__(exc_type, exc_value, traceback)


def set_custom_excepthook():
    sys.excepthook = custom_excepthook
