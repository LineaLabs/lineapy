import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="l_list",
)
literal_1 = LiteralNode(
    value="save",
)
lookup_3 = LookupNode(
    name="getattr",
)
literal_2 = LiteralNode(
    value="lineapy",
)
lookup_4 = LookupNode(
    name="l_exec_statement",
)
literal_3 = LiteralNode(
    value="""while idx < len(x):
    result += x[idx]
    idx += 1""",
)
source_1 = SourceCode(
    code="""import lineapy
x = [1, 2, 3]
idx = 0
result = 0
while idx < len(x):
    result += x[idx]
    idx += 1

lineapy.save(result, \'result\')
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
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=5,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=1,
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=8,
        end_lineno=2,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    value=2,
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=11,
        end_lineno=2,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    value=3,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_4.id, literal_5.id, literal_6.id],
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=6,
        end_lineno=3,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    value=0,
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=9,
        end_lineno=4,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    value=0,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=7,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[literal_3.id],
    global_reads={"idx": literal_7.id, "result": literal_8.id, "x": call_2.id},
)
global_1 = GlobalNode(
    name="idx",
    call_id=call_3.id,
)
global_2 = GlobalNode(
    name="result",
    call_id=call_3.id,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_1.id],
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=21,
        end_lineno=9,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    value="result",
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    function_id=call_4.id,
    positional_args=[global_2.id, literal_9.id],
)
