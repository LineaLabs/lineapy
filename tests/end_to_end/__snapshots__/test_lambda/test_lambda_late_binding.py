import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""a = 10
b = lambda: a
a = 11
c = b()""",
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
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=2,
            col_offset=4,
            end_lineno=2,
            end_col_offset=13,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="l_exec_expr",
        ).id,
        positional_args=[
            LiteralNode(
                value="lambda: a",
            ).id
        ],
    ).id,
    global_reads={
        "a": LiteralNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=4,
                end_lineno=3,
                end_col_offset=6,
                source_code=source_1.id,
            ),
            value=11,
        ).id
    },
)
