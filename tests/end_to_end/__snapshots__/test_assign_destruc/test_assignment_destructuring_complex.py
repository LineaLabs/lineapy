import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_list",
)
lookup_2 = LookupNode(
    name="l_unpack_ex",
)
literal_1 = LiteralNode(
    value=1,
)
lookup_3 = LookupNode(
    name="getitem",
)
literal_2 = LiteralNode(
    value=1,
)
literal_3 = LiteralNode(
    value=0,
)
lookup_4 = LookupNode(
    name="getitem",
)
literal_4 = LiteralNode(
    value=2,
)
lookup_5 = LookupNode(
    name="getitem",
)
lookup_6 = LookupNode(
    name="l_list",
)
literal_5 = LiteralNode(
    value=0,
)
lookup_7 = LookupNode(
    name="l_unpack_sequence",
)
literal_6 = LiteralNode(
    value=0,
)
lookup_8 = LookupNode(
    name="getitem",
)
literal_7 = LiteralNode(
    value=1,
)
source_1 = SourceCode(
    code="""c = [[1, 2], 3]
[a, b], *rest = c""",
    location=PosixPath("[source file path]"),
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=6,
        end_lineno=1,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    value=1,
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=9,
        end_lineno=1,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    value=2,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=5,
        end_lineno=1,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_8.id, literal_9.id],
)
literal_10 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=13,
        end_lineno=1,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    value=3,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[call_1.id, literal_10.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_2.id, literal_1.id, literal_6.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_3.id, literal_2.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=lookup_8.id,
    positional_args=[call_3.id, literal_5.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[call_5.id, literal_4.id],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_6.id, literal_7.id],
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[call_6.id, literal_3.id],
)
