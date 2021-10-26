import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import math
import lineapy
a = 0
def my_function():
    global a
    a = math.factorial(5)
my_function()
lineapy.linea_publish(a, \'mutated a\')
""",
    location=PosixPath("[source file path]"),
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    library=Library(
        name="math",
    ),
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=0,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=6,
        end_col_offset=25,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="__exec__",
    ).id,
    positional_args=[
        LiteralNode(
            value="""def my_function():
    global a
    a = math.factorial(5)""",
        ).id,
        LiteralNode(
            value=False,
        ).id,
        LiteralNode(
            value="a",
        ).id,
        LiteralNode(
            value="my_function",
        ).id,
    ],
)
call_3 = CallNode(
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_1.id,
        LiteralNode(
            value=0,
        ).id,
    ],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        function_id=LookupNode(
            name="getitem",
        ).id,
        positional_args=[
            call_1.id,
            LiteralNode(
                value=1,
            ).id,
        ],
    ).id,
)
