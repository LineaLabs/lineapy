from datetime import datetime
from uuid import uuid4

from lineapy.data.types import (
    Node,
    SessionContext,
    SessionType,
)


def get_new_id():
    return uuid4()


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
    raise NotImplementedError
