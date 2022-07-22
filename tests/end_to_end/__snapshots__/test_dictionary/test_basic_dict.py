import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_dict",
)
lookup_2 = LookupNode(
    name="l_tuple",
)
lookup_3 = LookupNode(
    name="l_tuple",
)
source_1 = SourceCode(
    code="x = {'a': 1, 'b': 2}",
    location=PosixPath("[source file path]"),
)
literal_1 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=5,
        end_lineno=1,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    value="a",
)
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=10,
        end_lineno=1,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    value=1,
)
call_1 = CallNode(
    function_id=lookup_3.id,
    positional_args=[literal_1.id, literal_2.id],
)
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=13,
        end_lineno=1,
        end_col_offset=16,
        source_code=source_1.id,
    ),
    value="b",
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=18,
        end_lineno=1,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value=2,
)
call_2 = CallNode(
    function_id=lookup_2.id,
    positional_args=[literal_3.id, literal_4.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[call_1.id, call_2.id],
)
