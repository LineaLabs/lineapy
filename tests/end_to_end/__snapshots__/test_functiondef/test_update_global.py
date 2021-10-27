import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
a = 10
def f():
    global a
    a = 1
f()

lineapy.linea_publish(a, \'a\')
""",
    location=PosixPath("[source file path]"),
)
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=10,
)
global_2 = GlobalNode(
    name="a",
    call_id=CallNode(
        source_location=SourceLocation(
            lineno=6,
            col_offset=0,
            end_lineno=6,
            end_col_offset=3,
            source_code=source_1.id,
        ),
        function_id=GlobalNode(
            name="f",
            call_id=CallNode(
                source_location=SourceLocation(
                    lineno=3,
                    col_offset=0,
                    end_lineno=5,
                    end_col_offset=9,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="l_exec_statement",
                ).id,
                positional_args=[
                    LiteralNode(
                        value="""def f():
    global a
    a = 1""",
                    ).id
                ],
            ).id,
        ).id,
    ).id,
)
