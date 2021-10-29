"""
Copied from https://naleraphael.github.io/blog/posts/devlog_create_a_builtin_frame_object/
"""
import ctypes
from types import CodeType, FrameType

P_SIZE = ctypes.sizeof(ctypes.c_void_p)
IS_X64 = P_SIZE == 8

P_MEM_TYPE = ctypes.POINTER(ctypes.c_ulong if IS_X64 else ctypes.c_uint)

ctypes.pythonapi.PyFrame_New.argtypes = (
    P_MEM_TYPE,  # PyThreadState *tstate
    P_MEM_TYPE,  # PyCodeObject *code
    ctypes.py_object,  # PyObject *globals
    ctypes.py_object,  # PyObject *locals
)
ctypes.pythonapi.PyFrame_New.restype = ctypes.py_object  # PyFrameObject*

ctypes.pythonapi.PyThreadState_Get.argtypes = ()
ctypes.pythonapi.PyThreadState_Get.restype = P_MEM_TYPE


def create_frame(code: CodeType) -> FrameType:
    """
    Creates a new frame object from a code object.
    """

    return ctypes.pythonapi.PyFrame_New(
        ctypes.pythonapi.PyThreadState_Get(),  # thread state
        ctypes.cast(id(code), P_MEM_TYPE),  # a code object
        # Make sure not to set __file__ in the globals,
        # or else ipython will look at it and change the file name
        {},  # a dict of globals
        {},  # a dict of locals
    )
