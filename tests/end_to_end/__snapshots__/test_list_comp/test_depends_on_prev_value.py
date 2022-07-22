import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_exec_expr",
)
literal_1 = LiteralNode(
    value="[i + 1 for i in y]",
)
source_1 = SourceCode(
    code="""y = range(3)
x = [i + 1 for i in y]
""",
    location=PosixPath("[source file path]"),
)
lookup_2 = LookupNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    name="range",
)
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=10,
        end_lineno=1,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    value=3,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_2.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_1.id],
    global_reads={"y": call_1.id},
)
