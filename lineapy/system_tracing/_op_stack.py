"""
Modified from https://gist.github.com/crusaderky/cf0575cfeeee8faa1bb1b3480bc4a87a
"""
import sys
from ctypes import POINTER, Structure, c_ssize_t, c_void_p, py_object, sizeof
from typing import Any, Tuple

__all__ = ("OpStack",)


# TODO: Cleanup file to remove what I don't need


class Frame(Structure):
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


if sys.flags.debug:
    Frame._fields_ = (
        ("_ob_next", POINTER(py_object)),
        ("_ob_prev", POINTER(py_object)),
    ) + Frame._fields_

PTR_SIZE = sizeof(POINTER(py_object))
F_VALUESTACK_OFFSET = sizeof(Frame) - 2 * PTR_SIZE
F_STACKTOP_OFFSET = sizeof(Frame) - PTR_SIZE


class OpStack:
    __slots__ = ("_frame",)

    def __init__(self, frame):
        self._frame = Frame.from_address(id(frame))

    def __repr__(self) -> str:
        return "<OpStack>"

    def __getitem__(self, item: int) -> Any:
        if item < 0:
            return self._frame.f_stacktop[item]
