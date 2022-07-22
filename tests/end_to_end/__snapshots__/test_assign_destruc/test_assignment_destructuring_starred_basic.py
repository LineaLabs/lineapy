import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_list",
)
literal_1 = LiteralNode(
    value=1,
)
literal_2 = LiteralNode(
    value=1,
)
literal_3 = LiteralNode(
    value=2,
)
lookup_2 = LookupNode(
    name="getitem",
)
lookup_3 = LookupNode(
    name="l_unpack_ex",
)
lookup_4 = LookupNode(
    name="getitem",
)
literal_4 = LiteralNode(
    value=1,
)
lookup_5 = LookupNode(
    name="getitem",
)
literal_5 = LiteralNode(
    value=0,
)
source_1 = SourceCode(
    code="a, *b, c = [1, 2, 3]",
    location=PosixPath("[source file path]"),
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=12,
        end_lineno=1,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    value=1,
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=15,
        end_lineno=1,
        end_col_offset=16,
        source_code=source_1.id,
    ),
    value=2,
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=18,
        end_lineno=1,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value=3,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=11,
        end_lineno=1,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_6.id, literal_7.id, literal_8.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_1.id, literal_2.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[call_2.id, literal_5.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_2.id, literal_3.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_2.id, literal_4.id],
)
