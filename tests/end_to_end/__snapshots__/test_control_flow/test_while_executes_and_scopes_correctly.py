import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
x=[1,2,3]
idx=0
result = 0
while idx<len(x):
    result += x[idx]
    idx += 1

lineapy.save(result, \'result\')
""",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=7,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_exec_statement",
    ).id,
    positional_args=[
        LiteralNode(
            value="""while idx<len(x):
    result += x[idx]
    idx += 1""",
        ).id
    ],
    global_reads={
        "idx": LiteralNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=4,
                end_lineno=3,
                end_col_offset=5,
                source_code=source_1.id,
            ),
            value=0,
        ).id,
        "result": LiteralNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=9,
                end_lineno=4,
                end_col_offset=10,
                source_code=source_1.id,
            ),
            value=0,
        ).id,
        "x": CallNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=2,
                end_lineno=2,
                end_col_offset=9,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_list",
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=3,
                        end_lineno=2,
                        end_col_offset=4,
                        source_code=source_1.id,
                    ),
                    value=1,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=5,
                        end_lineno=2,
                        end_col_offset=6,
                        source_code=source_1.id,
                    ),
                    value=2,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=7,
                        end_lineno=2,
                        end_col_offset=8,
                        source_code=source_1.id,
                    ),
                    value=3,
                ).id,
            ],
        ).id,
    },
)
global_1 = GlobalNode(
    name="idx",
    call_id=call_2.id,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=9,
            col_offset=0,
            end_lineno=9,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            ImportNode(
                source_location=SourceLocation(
                    lineno=1,
                    col_offset=0,
                    end_lineno=1,
                    end_col_offset=14,
                    source_code=source_1.id,
                ),
                name="lineapy",
                version="",
                package_name="lineapy",
            ).id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        GlobalNode(
            name="result",
            call_id=call_2.id,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=9,
                col_offset=21,
                end_lineno=9,
                end_col_offset=29,
                source_code=source_1.id,
            ),
            value="result",
        ).id,
    ],
)
