from datetime import datetime
from uuid import uuid4

from lineapy.data.types import (
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
