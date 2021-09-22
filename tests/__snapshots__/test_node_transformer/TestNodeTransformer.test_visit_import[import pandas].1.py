import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="import pandas",
    session_name=None,
    user_name=None,
    hardware_spec=None,
    libraries=[
        Library(
            id=get_new_id(),
            name="pandas",
            version=None,
            path=None,
        ),
    ],
)
import_1 = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=13,
    library=Library(
        id=get_new_id(),
        name="pandas",
        version=None,
        path=None,
    ),
    attributes=None,
    alias=None,
    module=None,
)
