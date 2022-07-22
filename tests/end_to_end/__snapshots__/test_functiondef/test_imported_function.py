import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
literal_1 = LiteralNode(
    value="save",
)
literal_2 = LiteralNode(
    value="lineapy",
)
literal_3 = LiteralNode(
    value="math",
)
lookup_2 = LookupNode(
    name="getattr",
)
lookup_3 = LookupNode(
    name="l_import",
)
literal_4 = LiteralNode(
    value="""def my_function():
    global a
    a = math.factorial(5)""",
)
lookup_4 = LookupNode(
    name="l_exec_statement",
)
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
import_1 = ImportNode(
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
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_2.id],
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    name="math",
    version="",
    package_name="math",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[literal_3.id],
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=0,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=6,
        end_col_offset=25,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[literal_4.id],
)
global_1 = GlobalNode(
    name="my_function",
    call_id=call_3.id,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=global_1.id,
    global_reads={"math": call_2.id},
)
global_2 = GlobalNode(
    name="a",
    call_id=call_4.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_1.id, literal_1.id],
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=16,
        end_lineno=9,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="a",
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_5.id,
    positional_args=[global_2.id, literal_6.id],
)
