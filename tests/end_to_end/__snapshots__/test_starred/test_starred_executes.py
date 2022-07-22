import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_exec_statement",
)
lookup_2 = LookupNode(
    name="l_dict",
)
lookup_3 = LookupNode(
    name="l_tuple",
)
literal_1 = LiteralNode(
    value="""def func(a,b):
    return a+b""",
)
lookup_4 = LookupNode(
    name="l_tuple",
)
source_1 = SourceCode(
    code="""def func(a,b):
    return a+b

args = {\'a\':1, \'b\':2}
ret = func(**args)
""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=2,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_1.id],
)
global_1 = GlobalNode(
    name="func",
    call_id=call_1.id,
)
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=8,
        end_lineno=4,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    value="a",
)
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=12,
        end_lineno=4,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    value=1,
)
call_2 = CallNode(
    function_id=lookup_3.id,
    positional_args=[literal_2.id, literal_3.id],
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=15,
        end_lineno=4,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    value="b",
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=19,
        end_lineno=4,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    value=2,
)
call_3 = CallNode(
    function_id=lookup_4.id,
    positional_args=[literal_4.id, literal_5.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=7,
        end_lineno=4,
        end_col_offset=21,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_2.id, call_3.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=6,
        end_lineno=5,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    function_id=global_1.id,
    keyword_args={"**": call_4.id},
)
