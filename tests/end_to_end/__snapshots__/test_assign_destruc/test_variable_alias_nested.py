import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_alias",
)
lookup_2 = LookupNode(
    name="l_alias",
)
source_1 = SourceCode(
    code="""a = 0
b = a
c = b""",
    location=PosixPath("[source file path]"),
)
literal_1 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=0,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_1.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_1.id],
)
