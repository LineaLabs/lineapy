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
lookup_4 = LookupNode(
    name="l_tuple",
)
lookup_5 = LookupNode(
    name="l_tuple",
)
lookup_6 = LookupNode(
    name="l_tuple",
)
lookup_7 = LookupNode(
    name="l_dict_kwargs_sentinel",
)
call_1 = CallNode(
    function_id=lookup_7.id,
)
lookup_8 = LookupNode(
    name="l_dict",
)
lookup_9 = LookupNode(
    name="l_tuple",
)
source_1 = SourceCode(
    code="x = {1: 2, 2:2, **{1: 3, 2: 3}, 1: 4}",
    location=PosixPath("[source file path]"),
)
literal_1 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=5,
        end_lineno=1,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=1,
)
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=8,
        end_lineno=1,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    value=2,
)
call_2 = CallNode(
    function_id=lookup_6.id,
    positional_args=[literal_1.id, literal_2.id],
)
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=11,
        end_lineno=1,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    value=2,
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=13,
        end_lineno=1,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    value=2,
)
call_3 = CallNode(
    function_id=lookup_2.id,
    positional_args=[literal_3.id, literal_4.id],
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=19,
        end_lineno=1,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    value=1,
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=22,
        end_lineno=1,
        end_col_offset=23,
        source_code=source_1.id,
    ),
    value=3,
)
call_4 = CallNode(
    function_id=lookup_5.id,
    positional_args=[literal_5.id, literal_6.id],
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=25,
        end_lineno=1,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    value=2,
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=28,
        end_lineno=1,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    value=3,
)
call_5 = CallNode(
    function_id=lookup_3.id,
    positional_args=[literal_7.id, literal_8.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=18,
        end_lineno=1,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    function_id=lookup_8.id,
    positional_args=[call_4.id, call_5.id],
)
call_7 = CallNode(
    function_id=lookup_9.id,
    positional_args=[call_1.id, call_6.id],
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=32,
        end_lineno=1,
        end_col_offset=33,
        source_code=source_1.id,
    ),
    value=1,
)
literal_10 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=35,
        end_lineno=1,
        end_col_offset=36,
        source_code=source_1.id,
    ),
    value=4,
)
call_8 = CallNode(
    function_id=lookup_4.id,
    positional_args=[literal_9.id, literal_10.id],
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=37,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[call_2.id, call_3.id, call_7.id, call_8.id],
)
