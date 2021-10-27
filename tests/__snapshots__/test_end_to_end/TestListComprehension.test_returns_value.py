import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="x = [i + 1 for i in range(3)]",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_exec_expr",
    ).id,
    positional_args=[
        LiteralNode(
            value="[i + 1 for i in range(3)]",
        ).id
    ],
)
