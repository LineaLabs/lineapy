from ast import AST
from datetime import datetime
from astpretty import pformat
from typing import Optional, List

from lineapy.data.types import (
    SessionContext,
    SessionType,
)
from lineapy.utils import get_new_id


def get_new_session(libraries: Optional[List] = None) -> SessionContext:
    if libraries is None:
        libraries = []
    return SessionContext(
        id=get_new_id(),
        file_name="testing.py",
        environment_type=SessionType.SCRIPT,
        creation_time=datetime.now(),
        libraries=libraries,
    )


def reset_test_db():
    """
    # TODO @dhruv. Please have a simple way of tearing down the test database
    # You might have to add some configs to the LineaDBConfig, or pass in some path to the db etc.
    If unsure, please sync with @yifanwu
    """
    pass
    # raise NotImplementedError


def compare_ast(node1: AST, node2: AST):
    """
    Compare two AST trees, ignoring offset information.
    """
    s1 = pformat(node1, show_offsets=False)
    s2 = pformat(node2, show_offsets=False)
    return s1 == s2
