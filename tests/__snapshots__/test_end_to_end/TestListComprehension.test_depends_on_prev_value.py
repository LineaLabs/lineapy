import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""y = range(3)
x = [i + 1 for i in y]
""",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_exec_expr",
    ).id,
    positional_args=[
        LiteralNode(
            value="[i + 1 for i in y]",
        ).id
    ],
    global_reads={
        "y": CallNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=4,
                end_lineno=1,
                end_col_offset=12,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                source_location=SourceLocation(
                    lineno=1,
                    col_offset=4,
                    end_lineno=1,
                    end_col_offset=9,
                    source_code=source_1.id,
                ),
                name="range",
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=10,
                        end_lineno=1,
                        end_col_offset=11,
                        source_code=source_1.id,
                    ),
                    value=3,
                ).id
            ],
        ).id
    },
)
