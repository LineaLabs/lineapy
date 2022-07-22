import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_exec_expr",
)
literal_1 = LiteralNode(
    value="lambda x: x + a",
)
source_1 = SourceCode(
    code="""a = 10
b = lambda x: x + a
c = b(10)
""",
    location=PosixPath("[source file path]"),
)
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=10,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_1.id],
)
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=6,
        end_lineno=3,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    value=10,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=call_1.id,
    positional_args=[literal_3.id],
    global_reads={"a": literal_2.id},
)
