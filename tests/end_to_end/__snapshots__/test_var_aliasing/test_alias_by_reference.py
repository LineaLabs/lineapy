import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_list",
)
lookup_2 = LookupNode(
    name="getattr",
)
lookup_3 = LookupNode(
    name="not_",
)
lookup_4 = LookupNode(
    name="l_alias",
)
lookup_5 = LookupNode(
    name="contains",
)
lookup_6 = LookupNode(
    name="contains",
)
literal_1 = LiteralNode(
    value="append",
)
source_1 = SourceCode(
    code="""a = [1,2,3]
b = a
a.append(4)
c = 2
r1 = c in a
r2 = c not in a
s = sum(b)
""",
    location=PosixPath("[source file path]"),
)
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=5,
        end_lineno=1,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=1,
)
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=7,
        end_lineno=1,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    value=2,
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=9,
        end_lineno=1,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    value=3,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_2.id, literal_3.id, literal_4.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_1.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_1.id, literal_1.id],
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=9,
        end_lineno=3,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    value=4,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=call_3.id,
    positional_args=[literal_5.id],
)
mutate_1 = MutateNode(
    source_id=call_1.id,
    call_id=call_4.id,
)
mutate_2 = MutateNode(
    source_id=call_2.id,
    call_id=call_4.id,
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=2,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=5,
        end_lineno=5,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[mutate_1.id, literal_6.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=5,
        end_lineno=6,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[mutate_1.id, literal_6.id],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=5,
        end_lineno=6,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_6.id],
)
lookup_7 = LookupNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=4,
        end_lineno=7,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    name="sum",
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=4,
        end_lineno=7,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[mutate_2.id],
)
