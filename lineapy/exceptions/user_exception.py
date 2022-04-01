from __future__ import annotations

from dataclasses import dataclass
from types import FrameType, TracebackType
from typing import Callable, Iterable, Optional, Union

from lineapy.exceptions.create_frame import create_frame
from lineapy.exceptions.flag import REWRITE_EXCEPTIONS


class UserException(Exception):
    """
    Create a traceback based on an original traceback with a number of changes
    applied to it.
    """

    __cause__: Exception

    def __init__(self, cause: Exception, *changes: TracebackChange):
        if REWRITE_EXCEPTIONS:
            apply_changes(cause, changes)

        self.__cause__ = cause


def apply_changes(exc: Exception, changes: Iterable[TracebackChange]) -> None:
    """
    Update an exception's traceback with the changes provided.
    """
    tb = exc.__traceback__
    for change in changes:
        tb = change.execute(tb)
    exc.__traceback__ = tb


@dataclass
class RemoveFrames:
    """
    Remove n frames from the top
    """

    n: int

    def execute(
        self, traceback: Optional[TracebackType]
    ) -> Optional[TracebackType]:
        for _ in range(self.n):
            assert traceback
            traceback = traceback.tb_next
        return traceback


@dataclass
class AddFrame:
    """
    Add a dummy frame with a filename and linenumber.
    """

    filename: str
    lineno: int

    def execute(self, traceback: Optional[TracebackType]) -> TracebackType:
        code = compile("", self.filename, "exec")

        return TracebackType(
            traceback,
            create_frame(code),
            0,
            self.lineno,
        )


@dataclass
class RemoveFramesWhile:
    """
    Remove frames while the predicate is true
    """

    predicate: Callable[[FrameType], bool]

    def execute(
        self, traceback: Optional[TracebackType]
    ) -> Optional[TracebackType]:
        while traceback and self.predicate(traceback.tb_frame):
            traceback = traceback.tb_next
        return traceback


TracebackChange = Union[RemoveFrames, AddFrame, RemoveFramesWhile]
