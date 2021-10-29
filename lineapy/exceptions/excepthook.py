import sys

from lineapy.exceptions.flag import REWRITE_EXCEPTIONS
from lineapy.exceptions.user_exception import UserException


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
    if REWRITE_EXCEPTIONS:
        sys.excepthook = custom_excepthook
