import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_exec_statement",
)
lookup_2 = LookupNode(
    name="getitem",
)
literal_1 = LiteralNode(
    value=0,
)
literal_2 = LiteralNode(
    value=1,
)
literal_3 = LiteralNode(
    value="""def func():
    for i in range(3):
        for j in range(3):
            yield (i,j), 10""",
)
literal_4 = LiteralNode(
    value=2,
)
lookup_3 = LookupNode(
    name="getitem",
)
lookup_4 = LookupNode(
    name="l_unpack_sequence",
)
source_1 = SourceCode(
    code="""def func():
    for i in range(3):
        for j in range(3):
            yield (i,j), 10

ind, patch = zip(*func())""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=4,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_3.id],
)
global_1 = GlobalNode(
    name="func",
    call_id=call_1.id,
)
lookup_5 = LookupNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=13,
        end_lineno=6,
        end_col_offset=16,
        source_code=source_1.id,
    ),
    name="zip",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=18,
        end_lineno=6,
        end_col_offset=24,
        source_code=source_1.id,
    ),
    function_id=global_1.id,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=13,
        end_lineno=6,
        end_col_offset=25,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[*call_2.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=25,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_3.id, literal_4.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=25,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_4.id, literal_2.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=25,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_4.id, literal_1.id],
)
