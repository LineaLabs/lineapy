from ast import AST
from datetime import datetime
from os import remove
from typing import Optional, List

from astpretty import pformat

from lineapy.data.types import (
    SessionContext,
    SessionType,
)
from lineapy.utils import get_new_id


def get_new_session(code: str, libraries: Optional[List] = None) -> SessionContext:
    if libraries is None:
        libraries = []
    return SessionContext(
        id=get_new_id(),
        file_name="testing.py",
        environment_type=SessionType.SCRIPT,
        creation_time=datetime.now(),
        libraries=libraries,
        code=code,
    )


def reset_test_db(sqlite_uri: str):
    """ """
    try:
        r = sqlite_uri.split("///")
        remove(r[1])
        return True
    except:
        return False


def compare_ast(node1: AST, node2: AST):
    """
    Compare two AST trees, ignoring offset information.
    """
    s1 = pformat(node1, show_offsets=False)
    s2 = pformat(node2, show_offsets=False)
    return s1 == s2
