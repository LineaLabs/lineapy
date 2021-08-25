from datetime import datetime
from ast import AST
from itertools import starmap

from lineapy.utils import get_new_id

from lineapy.data.types import (
    SessionContext,
    SessionType,
)


def get_new_session(libraries):
    return SessionContext(
        uuid=get_new_id(),
        file_name="testing.py",
        environment_type=SessionType.SCRIPT,
        creation_time=datetime.now(),
        libraries=libraries,
    )


def reset_test_db():
    """
    # TODO @dhruv. Please have a simple way of tearing down the test database
    # You might have to add some configs to the LineaDBConfig, or pass in some path to the db etc. If unsure, please sync with @yifanwu
    """
    pass
    # raise NotImplementedError


# adapted from https://stackoverflow.com/questions/3312989/elegant-way-to-test-python-asts-for-equality-not-reference-or-object-identity
def compare_ast(node1: AST, node2: AST):
    # internal_warning_log("Not implemented error")
    if type(node1) is not type(node2):
        return False
    if isinstance(node1, AST):
        # FIXME: not sure why this var is not happy
        for k, v in vars(node1).iteritems():
            if k in ("lineno", "col_offset", "ctx"):
                continue
            if not compare_ast(v, getattr(node2, k)):
                return False
        return True
    elif isinstance(node1, list):
        return all(starmap(compare_ast, zip(node1, node2)))
    else:
        return node1 == node2
