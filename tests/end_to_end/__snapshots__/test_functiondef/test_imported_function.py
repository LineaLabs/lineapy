import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
import math
a = 0
def my_function():
    global a
    a = math.factorial(5)
my_function()

lineapy.save(a, \'a\')
""",
    location=PosixPath("[source file path]"),
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    library=Library(
        name="math",
    ),
)
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=0,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=GlobalNode(
        name="my_function",
        call_id=CallNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=0,
                end_lineno=6,
                end_col_offset=25,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_exec_statement",
            ).id,
            positional_args=[
                LiteralNode(
                    value="""def my_function():
    global a
    a = math.factorial(5)""",
                ).id
            ],
        ).id,
    ).id,
    global_reads={"math": import_2.id},
)
mutate_1 = MutateNode(
    source_id=import_2.id,
    call_id=call_2.id,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=20,
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
                library=Library(
                    name="lineapy",
                ),
            ).id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        GlobalNode(
            name="a",
            call_id=call_2.id,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=9,
                col_offset=16,
                end_lineno=9,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="a",
        ).id,
    ],
)
