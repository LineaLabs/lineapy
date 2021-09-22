from lineapy.data.types import *
from lineapy.utils import get_new_id

session_id = get_new_id()
import_1 = ImportNode(
    id=get_new_id(),
    session_id=session_id,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=29,
    library=Library(
        id=get_new_id(),
        name="math",
        version=None,
        path=None,
    ),
    attributes={"power": "pow"},
    alias=None,
    module=None,
)
