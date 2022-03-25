"""
Modified from https://gist.github.com/crusaderky/cf0575cfeeee8faa1bb1b3480bc4a87a,
to remove all feature besides getting items from the top of the stack.
"""
import sys
from ctypes import POINTER, Structure, c_ssize_t, c_void_p, py_object
from types import FrameType
from typing import Any, Tuple

__all__ = ("OpStack",)


class Frame(Structure):
    """
    ctypes Structre (https://docs.python.org/3/library/ctypes.html#structures-and-unions) for a Python frame
    object, so we can access the top of the stack.
    """

    _fields_: Tuple[Tuple[str, object], ...] = (
        ("ob_refcnt", c_ssize_t),
        ("ob_type", c_void_p),
        ("ob_size", c_ssize_t),
        ("f_back", c_void_p),
        ("f_code", c_void_p),
        ("f_builtins", POINTER(py_object)),
        ("f_globals", POINTER(py_object)),
        ("f_locals", POINTER(py_object)),
        ("f_valuestack", POINTER(py_object)),
        ("f_stacktop", POINTER(py_object)),
    )


# The frame object has additional fields in debug mode
if sys.flags.debug:
    Frame._fields_ = (
        ("_ob_next", POINTER(py_object)),
        ("_ob_prev", POINTER(py_object)),
    ) + Frame._fields_


class OpStack:
    def __init__(self, frame: FrameType):
        self._frame = Frame.from_address(id(frame))

    def __getitem__(self, item: int) -> Any:
        if item < 0:
            return self._frame.f_stacktop[item]
