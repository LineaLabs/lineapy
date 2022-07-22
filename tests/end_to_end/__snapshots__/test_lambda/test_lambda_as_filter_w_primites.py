import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_list",
)
literal_1 = LiteralNode(
    value="lambda x: x%2==0",
)
lookup_2 = LookupNode(
    name="l_exec_expr",
)
source_1 = SourceCode(
    code="""list_1 = [1,2,3,4,5,6,7,8,9]
list_2 = list(filter(lambda x: x%2==0, list_1))
""",
    location=PosixPath("[source file path]"),
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
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=12,
        end_lineno=1,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    value=2,
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=14,
        end_lineno=1,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    value=3,
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=16,
        end_lineno=1,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    value=4,
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=18,
        end_lineno=1,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value=5,
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=20,
        end_lineno=1,
        end_col_offset=21,
        source_code=source_1.id,
    ),
    value=6,
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=22,
        end_lineno=1,
        end_col_offset=23,
        source_code=source_1.id,
    ),
    value=7,
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=24,
        end_lineno=1,
        end_col_offset=25,
        source_code=source_1.id,
    ),
    value=8,
)
literal_10 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=26,
        end_lineno=1,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    value=9,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=9,
        end_lineno=1,
        end_col_offset=28,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[
        literal_2.id,
        literal_3.id,
        literal_4.id,
        literal_5.id,
        literal_6.id,
        literal_7.id,
        literal_8.id,
        literal_9.id,
        literal_10.id,
    ],
)
lookup_3 = LookupNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=9,
        end_lineno=2,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    name="list",
)
lookup_4 = LookupNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=14,
        end_lineno=2,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    name="filter",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=21,
        end_lineno=2,
        end_col_offset=37,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_1.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=14,
        end_lineno=2,
        end_col_offset=46,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_2.id, call_1.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=9,
        end_lineno=2,
        end_col_offset=47,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_3.id],
)
