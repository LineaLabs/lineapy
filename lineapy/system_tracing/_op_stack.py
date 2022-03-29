"""
Modified from https://gist.github.com/crusaderky/cf0575cfeeee8faa1bb1b3480bc4a87a,
to remove all feature besides getting items from the top of the stack.
"""
import sys
from ctypes import POINTER, Structure, c_ssize_t, c_void_p, py_object, sizeof
from types import FrameType
from typing import Any, Tuple

__all__ = ("OpStack",)


class Frame(Structure):
    """
    ctypes Structure (https://docs.python.org/3/library/ctypes.html#structures-and-unions) for a Python frame
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

PTR_SIZE = sizeof(POINTER(py_object))
F_VALUESTACK_OFFSET = sizeof(Frame) - 2 * PTR_SIZE
F_STACKTOP_OFFSET = sizeof(Frame) - PTR_SIZE


class OpStack:
    """
    Only support negative access
    """

    def __init__(self, frame: FrameType):
        self._frame = Frame.from_address(id(frame))
        stack_start_addr = c_ssize_t.from_address(
            id(frame) + F_VALUESTACK_OFFSET
        ).value
        stack_top_addr = c_ssize_t.from_address(
            id(frame) + F_STACKTOP_OFFSET
        ).value
        self._len = (stack_top_addr - stack_start_addr) // PTR_SIZE

    def __getitem__(self, item: int) -> Any:
        if item < -self._len or item >= 0:
            raise IndexError(item)
        if item < 0:
            return self._frame.f_stacktop[item]
