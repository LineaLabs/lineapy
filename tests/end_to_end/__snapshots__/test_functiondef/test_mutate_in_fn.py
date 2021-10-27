import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
def f():
    a.append(1)
a = []
f()

lineapy.save(a, \'a\')
""",
    location=PosixPath("[source file path]"),
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=3,
        source_code=source_1.id,
    ),
    function_id=GlobalNode(
        name="f",
        call_id=CallNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=0,
                end_lineno=3,
                end_col_offset=15,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_exec_statement",
            ).id,
            positional_args=[
                LiteralNode(
                    value="""def f():
    a.append(1)""",
                ).id
            ],
        ).id,
    ).id,
    global_reads={
        "a": CallNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=4,
                end_lineno=4,
                end_col_offset=6,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_list",
            ).id,
        ).id
    },
)
