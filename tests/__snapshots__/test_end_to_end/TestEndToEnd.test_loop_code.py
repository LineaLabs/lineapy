import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
a = []
b = 0
for x in range(9):
    a.append(x)
    b+=x
x = sum(a)
y = x + b
lineapy.save(y, \'y\')
""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_list",
    ).id,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=6,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_exec_statement",
    ).id,
    positional_args=[
        LiteralNode(
            value="""for x in range(9):
    a.append(x)
    b+=x""",
        ).id
    ],
    global_reads={
        "a": call_1.id,
        "b": LiteralNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=4,
                end_lineno=3,
                end_col_offset=5,
                source_code=source_1.id,
            ),
            value=0,
        ).id,
    },
)
global_2 = GlobalNode(
    name="x",
    call_id=call_2.id,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=4,
        end_lineno=8,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="add",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=7,
                col_offset=4,
                end_lineno=7,
                end_col_offset=10,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                source_location=SourceLocation(
                    lineno=7,
                    col_offset=4,
                    end_lineno=7,
                    end_col_offset=7,
                    source_code=source_1.id,
                ),
                name="sum",
            ).id,
            positional_args=[call_1.id],
        ).id,
        GlobalNode(
            name="b",
            call_id=call_2.id,
        ).id,
    ],
)
