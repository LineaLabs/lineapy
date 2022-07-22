import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="getattr",
)
literal_1 = LiteralNode(
    value="imag",
)
lookup_2 = LookupNode(
    name="eq",
)
source_1 = SourceCode(
    code="""a = 1
b=a.imag == 1""",
    location=PosixPath("[source file path]"),
)
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=1,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=2,
        end_lineno=2,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_2.id, literal_1.id],
)
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=12,
        end_lineno=2,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    value=1,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=2,
        end_lineno=2,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_1.id, literal_3.id],
)
