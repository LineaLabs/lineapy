import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_exec_statement",
)
literal_1 = LiteralNode(
    value="""def func(*args):
    retobv = (m for m in args)
    return list(retobv)""",
)
source_1 = SourceCode(
    code="""def func(*args):
    retobv = (m for m in args)
    return list(retobv)

name = "myname"
it = iter(name)
print(next(it))
x = func(*it)
""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=3,
        end_col_offset=23,
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
        lineno=5,
        col_offset=7,
        end_lineno=5,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    value="myname",
)
lookup_2 = LookupNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=5,
        end_lineno=6,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    name="iter",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=5,
        end_lineno=6,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_2.id],
)
lookup_3 = LookupNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    name="print",
)
lookup_4 = LookupNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=6,
        end_lineno=7,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    name="next",
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=6,
        end_lineno=7,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_2.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_3.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=4,
        end_lineno=8,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=global_1.id,
    positional_args=[*call_2.id],
)
